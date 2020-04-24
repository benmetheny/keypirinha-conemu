# Keypirinha | A semantic launcher for Windows | http://keypirinha.com

import keypirinha as kp
import keypirinha_util as kpu
import os
import os.path
import xml.etree.ElementTree as ET
import shutil

class ConEmu(kp.Plugin):
    """
    Launch ConEmu tasks.

    This plugin will load all configured tasks from the ConEmu.xml configuration file.
    ConEmu path is attempted to be located via searching PATH environment variable, if
    not set in PATH this value must be configured manually.
    """

    DEFAULT_EXENAME = "ConEmu.exe"
    DEFAULT_XMLNAME = "ConEmu.xml"
    DEFAULT_ICONKEY = "DEFAULT"

    def __init__(self):
        super().__init__()

        self._icons = {}
        self._tasks = []


    def on_catalog(self):
        self._read_config()
        if self._conemu_path is None:
            self.info("Path to ConEmu could not be located and must be added to the configuration manually.")
            return
        if not os.path.isfile(os.path.join(self._conemu_path,self._xml_name)):
            return

        self._load_tasks()
        catalog = []
        for task in self._tasks:
            catalog.append(self.create_item(
                category = kp.ItemCategory.REFERENCE,
                label=self._task_prefix + task["name"],
                short_desc=task["description"],
                target=task["command"],
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS,
                icon_handle=self._icons[task["icon"]]
            ))
        self.set_catalog(catalog)

    def on_execute(self, item, action):
        if item.category() == kp.ItemCategory.REFERENCE:
            kpu.shell_execute(os.path.join(self._conemu_path,self._exe_name),args="-run " + item.label().replace(self._task_prefix,""))


    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.info("ConEmu plugin configuration changed, rebuilding catalog...")
            self.on_catalog()


    def _read_config(self):
        settings = self.load_settings()

        self._exe_name = settings.get_stripped("exe_name",section="main",fallback=self.DEFAULT_EXENAME)
        self._xml_name = settings.get_stripped("xml_name",section="main",fallback=self.DEFAULT_XMLNAME)
        self._conemu_path = settings.get_stripped("path",section="main",fallback=self._autodetect_path())
        self._task_prefix = settings.get("task_prefix",section="main",unquote=True)


    def _load_tasks(self):
        if self._icons:
            for key in self._icons:
                try:
                    self._icons[key].free()
                except:
                    self.err("Exception while unloading icons!")

        xmlFilePath = os.path.join(self._conemu_path,self._xml_name)
        self.info("ConEmu plugin is loading tasks from: " + xmlFilePath)
        tree = ET.parse(xmlFilePath)
        taskNodes = tree.getroot().findall(".//key[@name='Tasks']/key")
        self._tasks = []
        exePath = os.path.join(self._conemu_path,self._exe_name)
        self._icons = {self.DEFAULT_ICONKEY:self.load_icon("@" + exePath + ",0")}
        cachePath = self.get_package_cache_path(True)
        for taskNode in taskNodes:
            task = {}
            for taskDetails in taskNode.iter("value"):
                if taskDetails.attrib["name"] == "Name":
                    task["name"] = taskDetails.attrib["data"]
                    task["command"] = exePath + ' -run "' + taskDetails.attrib["data"] + '"'
                if taskDetails.attrib["name"] == "Cmd1":
                    task["description"] = taskDetails.attrib["data"]
                if taskDetails.attrib["name"] == "GuiArgs":
                    expandedPath = os.path.expandvars(taskDetails.attrib["data"].split(' ')[-1]).replace('"','')
                    if not os.path.isfile(expandedPath):
                        task["icon"] = self.DEFAULT_ICONKEY
                        continue
                    
                    fileName = os.path.split(expandedPath)[1]
                    task["icon"] = fileName
                    if not fileName in self._icons:
                        #need to copy icons to plugin cache directory in order to load them
                        if not os.path.isfile(os.path.join(cachePath,fileName)):
                            shutil.copyfile(expandedPath,os.path.join(cachePath,fileName))
                        cachedIconUri = "cache://ConEmu/" + fileName
                        try:
                            self._icons[fileName] = self.load_icon(cachedIconUri)
                        except:
                            task["icon"] = self.DEFAULT_ICONKEY
            self._tasks.append(task)

    
    def _autodetect_path(self):
        path_dirs = [
            os.path.expandvars(p.strip())
                for p in os.getenv("PATH", "").split(";") if p.strip() ]

        for path_dir in path_dirs:
            exe_file = os.path.join(path_dir, self._exe_name)
            if os.path.exists(exe_file):
                self.info("ConEmu plugin located base directory at: " + path_dir)
                return path_dir

        return None
