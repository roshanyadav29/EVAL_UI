from codes.complete_gui import RUN
import jaraco.windows.api.memory
import jaraco.windows.filesystem
import jaraco.windows.filesystem as fs; fs.patch_os_module()

RUN()
