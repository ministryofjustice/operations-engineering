# Source Files

The source files in this folder are html.md.erb files.

This stands for embedded ruby and markdown turned into html.

The files are not written in HTML instead Markdown is used.

The syntax is Markdown, more details can be found [here](https://daringfireball.net/projects/markdown/). 

A hash represents a header `<h1>, <h2>,` etc.

See this [link](https://tdt-documentation.london.cloudapps.digital/write_docs/content/#write-your-content) on how to write items in the Markdown files.

Files are linked to each other using this approach `[text](documentation/folder-name/file-name.html)` or `[text](folder-name/file-name.html)`

Filenames must be `[something].html.md.erb`

Middleman is used to create the html files for the website.

It uses the index.html.md.erb file as the entry point.

The other .html.md.erb files are seperate entities from each other and not used as a structure as seen in other [Middleman projects](https://tdt-documentation.london.cloudapps.digital/configure_project/structure_docs/#structure-your-documentation).

The Markdown syntax may use [kramdown](https://kramdown.gettalong.org/syntax.html) format.
