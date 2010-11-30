# Copyright 2010 Thomas Beverley (http://github.com/Thomas101). All rights reserved.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import datetime
import inspect
import os
import json
import shutil
import sys

__fileLocation__ = os.path.join(os.getcwd(), os.path.split(inspect.currentframe().f_code.co_filename)[0])

def compileAll(config):
    '''
    Compiles everything based on what has been provided
    @param config: the config file describing what to output
    '''
    
    start = datetime.datetime.utcnow()
    
    #Do the javascript first
    jsMax = os.path.join(config['js']['output'], config['project'] + ".js")
    jsMin = os.path.join(config['js']['output'], config['project'] + ".min.js")
    jsFiles = findFiles(config['js']['libs'], 'js', config['js']['excludes'])
    jsFiles.extend(findFiles(config['js']['dirs'], 'js', config['js']['excludes']))
    
    # We need to remove duplicates. Ideally we would call set(jsFiles) but this
    # might change our ordering. Ordering is very important for the libraries
    # so we have to do it manually
    cleaned = []
    for f in jsFiles:
        if not f in cleaned:
            cleaned.append(f)
    jsFiles = cleaned
    
    if len(jsFiles):
        print "Found " + str(len(jsFiles)) + " JavaScript files..."
        print "  Combining into one super JavaScript"
        combineFiles(jsFiles, jsMax)
        
        print "  Compiling JavaScript"
        compileJs(jsMax, jsMin)
        
        if config['js']['removeExpanded']:
            os.remove(jsMax)
            
        print ("Complete!")
    else:
        print "No JavaScript files found"
        
    #Do the css second
    cssMax = os.path.join(config['css']['output'], config['project'] + ".css")
    cssMin = os.path.join(config['css']['output'], config['project'] + ".min.css")
    cssFiles = findFiles(config['css']['dirs'], 'css', config['css']['excludes'])
    cssFiles = set(cssFiles)

    if len(cssFiles):
        print "Found " + str(len(cssFiles)) + " CSS files..."
        print "  Combining into one CSS file"
        combineFiles(cssFiles, cssMax)

        print "  Minifying CSS"
        compileCss(cssMax, cssMin)

        if config['css']['removeExpanded']:
            os.remove(cssMax)

        print ("Complete!")
    else:
        print "No CSS files found"

    # Copy the static files across
    print "Copying static files"
    copyStatic(config['static'])
    print "Complete"

    end = datetime.datetime.utcnow()
    success((end-start).seconds)

def copyStatic(files):
    '''
    Copies files and directories from a to b
    @param files: the files to copy in the form of [{to:<>, from:<>}, ...]
    '''
    for i in files:
        toLoc = i['to']
        fromLoc = i['from']
        
        print "  copying " + fromLoc
        
        files = findFiles([fromLoc], '*', [])

        absFromPath = os.path.abspath(fromLoc)
        absToPath = os.path.abspath(toLoc)

        for fileFrom in files:
            fileFrom = os.path.abspath(fileFrom)
            fileTo = fileFrom.replace(absFromPath, absToPath)
            if not os.path.exists(os.path.split(fileTo)[0]):
                os.makedirs(os.path.split(fileTo)[0])
            shutil.copy(fileFrom, fileTo)
    

def findFiles(directories, fileType, exclude):
    '''
    Finds files of a certain type
    @param directories: the directory to look in
    @param fileType: the type of files to find
    @param exclude: a list of files to exclude
    @return a list of files found
    '''
    files = []
    
    while directories:
        next = directories[0]
        directories = directories[1:]
        
        if os.path.isdir(next):
            for f in os.listdir(next):
                directories.append(os.path.join(next, f))
        elif os.path.isfile(next):
            isExcluded = False
            for e in exclude:
                if os.path.samefile(e, next):
                    isExcluded = True
                    break
            if (isExcluded == False and os.path.split(next)[1].startswith(".") == False) and (os.path.splitext(next)[1] == "." + fileType or fileType == "*"):
                files.append(os.path.abspath(next))
    return files
        

def combineFiles(inputList, outputFile):
    '''
    Combines files into one single file
    @param inputList: a list of all files to combine
    @param outputFile: the output file to place the files in
    '''
    if not os.path.exists(os.path.split(outputFile)[0]):
        os.makedirs(os.path.split(outputFile)[0])
        
    outputFile = open(outputFile, 'w')
    for path in inputList:
        openFile = open(path)
        outputFile.write(openFile.read() + "\n")
        openFile.close()
    
    outputFile.close()

def compileJs(inputFile, outputFile):
    '''
    Compiles a javascript file
    @param inputFile: the file to compile
    @param outputFile: the location in which to place the output file
    '''
    if not os.path.exists(os.path.split(outputFile)[0]):
        os.makedirs(os.path.split(outputFile)[0])
        
    options = [
        '--js=' + inputFile,
        '--js_output_file=' + outputFile,
        '--warning_level=QUIET']
    exitState = os.system(
        'java -jar %s %s' % (os.path.join(__fileLocation__, "closure_compiler.jar"), ' '.join(options)))
    if exitState != 0:
        failure(exitState, "Exit state from closure compiler was " + str(exitState))

def compileCss(inputFile, outputFile):
    '''
    Compiles a css file
    @param inputFile: the file to compile
    @param outputFile: the location in which to place the output file
    '''
    if not os.path.exists(os.path.split(outputFile)[0]):
        os.makedirs(os.path.split(outputFile)[0])
        
    options = ['-o ' + outputFile, '--type css']
    exitState = os.system(
        'java -jar "%s" %s "%s"' % (os.path.join(__fileLocation__, "yuicompressor-2.4.2.jar"), ' '.join(options), inputFile))    
    if exitState != 0:
        failure(exitState, "Exit state from YUI compiler was " + str(exitState))

def printUsage():
    '''
    Prints the usage out
    '''
    print "\n".join([
        "Javascript and css compiler\n",
        "Example usage: 'python compiler.py manifest.json'",
        "\n",
        "manifest.json is a JSON file accepting the following structure",
        "{"
        "   project     : string:projectName='project',",
        "   js          : {"
        "       dirs                : array:directories=[],",
        "       libs                : array:directories=[],",
        "       excludes            : array:directories=[],",
        "       removeExpanded      : boolean:remove=False,",
        "       output              : string:outputPath='pwd',",
        "   },",
        "   css         : {",
        "       dirs                : array:directories=[],",
        "       excludes            : array:directories=[],",
        "       removeExpanded      : boolean:remove=False,",
        "       output              : string:outputPath='pwd',",
        "   },",
        "   static      : array:objects:to,from=[],",
        "},",
    ])

def failure(code, reason):
    '''
    Terminates the script
    @param code: the exit code
    @param reason: a plain text reason
    '''
    print "*******************************************************************"
    print "COMPILE FAILURE:"
    print reason
    print "*******************************************************************"
    exit(code)

def success(secs):
    '''
    Terminates the script
    @param secs: the seconds it ran for
    '''
    print "*******************************************************************"
    print "COMPILE SUCCESS in " + str(secs) + " seconds"
    print "*******************************************************************"
    exit(0)

if __name__ == "__main__":
    #Check there are enough arguments
    if len(sys.argv) != 2:
        printUsage()
        failure(1, "Incorrect amount of arguments supplied")
    
    #Load the manifest file
    manifestPath = os.path.abspath(sys.argv[1])
    try:
        manifestFile = open(manifestPath)
        manifest = manifestFile.read()
        manifestFile.close()
    except IOError, ex:
        printUsage()
        failure(2, "Problem while reading manifest file")
    
    #Parse the manifest file
    try:
        manifest = json.loads(manifest)
    except ValueError, ex:
        printUsage()
        failure(3, "Unable to parse the manifest file")
        
    # Create the config
    config = {
        'project'   : manifest.get("project", "project"),
        'js'        : {
            'dirs'              : manifest.get('js', {}).get('dirs', []),
            'libs'              : manifest.get('js', {}).get('libs', []),
            'excludes'          : manifest.get('js', {}).get('excludes', []),
            'removeExpanded'    : manifest.get('js', {}).get('removeExpanded', False),
            'output'            : os.path.join(__fileLocation__, "compiled"),
        },
        'css'       : {
            'dirs'              : manifest.get('css', {}).get('dirs', []),
            'excludes'          : manifest.get('css', {}).get('excludes', []),
            'removeExpanded'    : manifest.get('css', {}).get('removeExpanded', False),
            'output'            : os.path.join(__fileLocation__, "compiled"),
        },
        'static'    : manifest.get('static', []),
    }
    
    # Do some jiggery pokery on the output files to ensure they are relative from the manifest
    if manifest.get('js', {}).get('output'):
        config['js']['output'] = os.path.join(os.path.split(manifestPath)[0], manifest['js']['output'])
    if manifest.get('css', {}).get('output'):
        config['css']['output'] = os.path.join(os.path.split(manifestPath)[0], manifest['css']['output'])

    #Filter all the paths to ensure they are not relative and fix if needed
    fromManifestPath = lambda a: [ os.path.join(os.path.split(manifestPath)[0], i) for i in a]
    config['js']['dirs'] = fromManifestPath(config['js']['dirs'])
    config['js']['libs'] = fromManifestPath(config['js']['libs'])
    config['js']['excludes'] = fromManifestPath(config['js']['excludes'])
    config['css']['dirs'] = fromManifestPath(config['css']['dirs'])
    config['css']['excludes'] = fromManifestPath(config['css']['excludes'])
    
    #Filter the static paths too
    for i in config['static']:
        i['to'] = os.path.join(os.path.split(manifestPath)[0], i['to'])
        i['from'] = os.path.join(os.path.split(manifestPath)[0], i['from'])
        
    #Attempt to delete the output directories
    
    #Go ahead and work on the files
    compileAll(config)