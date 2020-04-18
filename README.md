# Keypirinha Plugin: ConEmu
This is a package that extends the fast keystroke launcher keypirinha (http://keypirinha.com/) with
tasks defined in ConEmu configuration.

## Usage
Start typing the name of a task that is configured in ConEmu.

Executing a result from this plugin will launch the selected task in ConEmu

## Configuration
The plugin will walk each directory in the PATH environment variable to check for ConEmu.xml file, if found the directory will be used as the base directory for both lauching ConEmu.exe and loading ConEmu.xml to parse tasks.

If your ConEmu directory is not in PATH, it must be configured manually using the "path" setting. There are settings for "exe_name" and "xml_name" which default to "ConEmu.exe" and "ConEmu.xml" respectively.

Configuration setting "task_prefix" is a string which is prepended to the name of the task in the results window. It defaults to "ConEmu: " and can be set to an empty value.
