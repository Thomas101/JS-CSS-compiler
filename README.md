# JavaScript and CSS compiler

**Requirements: Java, Python**

This is a handy script that combines the closure compiler by Google (http://code.google.com/closure/compiler/) and the YUI compressor by Yahoo (http://developer.yahoo.com/yui/compressor/). It allows you to combine then minify your JavaScript and CSS into single files. Configuration is done through a manifest and thus this is a great script to call in your build scripts before deploying. Nothing too exciting but useful none the less!

## Usage

To use the compiler simply call:
    `python compiler.py <path_to_manifest>`

## Manifests

A manifest is just a file containing valid JSON. It describes how to compile your code

### Example

```js
{
    "project": "my_project",
    "js": {
        "dirs"          : ["js/"],
        "libs"          : [
                            "js/lib/jquery.js",
                            "js/lib/jquery-ui.js"
                            ],
        "excludes"      : ["js/test/file.js"],
        "removeExpanded": true,
        "output"        : "../compiled/"
    },
    "css": {
        "dirs"          : ["style/"],
        "excludes"      : [],
        "removeExpanded": true,
        "output"        : "../compiled/"
    },
    "static": [
        {"from" : "style/textures/",
        "to"    : "../compiled/textures/"}
    ]
}
```

### Explaination

* `project`:string='project' the name of your project

* `js.dirs`:array=[] the list of directories to include. Accepts directories and files.
* `js.libs`:array=[] a list of libraries to include. Accepts directories and files.
* `js.excludes`:array=[] list of files to exclude from the compilation
* `js.removeExpanded`:bool=false set to true to remove the non-minified versions of your code
* `js.output`:string: the location in which to output the JavaScript files

* `css.dirs`:array=[] the list of directories to include. Accepts directories and files.
* `css.excludes`:array=[] list of files to exclude from the compilation
* `css.removeExpanded`:bool=false set to true to remove the non-minified versions of your code
* `css.output`:string: the location in which to output the CSS files

* `static`:array=[] list of objects containing from and to keys. This defines where to copy files from and to. Accepts files and directories

### Notes

* Ensure that your JSON is valid. The easiest thing to do is build up an object and call an `object.string()` (or similar) method on it.
* If you do not provide values with default values the default will be used. Defaults are shown above
* Once compilation is complete you will have two versions of each file. The first for example is `project.js` and the second `project.min.js`. Setting `removeExpanded` to false removes the larger file (i.e. `project.js`)
* When combining JavaScript libraries are always added first and if the files are provided as opposed to directories they are applied in order. Therefore if you have libraries with dependencies just place them in order in the manifest file
