SRC_DIR = src
ADDON_NAME = wirebomb
INSTALL_ZIP_PATH = ./$(ADDON_NAME)-install.zip
INSTALL_SCRIPT_PATH = blender-install.py

.PHONY: all install clean

all:
	mkdir $(ADDON_NAME)
	cp $(SRC_DIR)/* LICENSE.md $(ADDON_NAME)
	zip -rm $(INSTALL_ZIP_PATH) $(ADDON_NAME)

install:
	@if [ ! -f $(INSTALL_ZIP_PATH) ]; then\
		echo "Error: Installation zip not found, did you forget to run ´make´?";\
		exit 1;\
	fi
	blender -b -P $(INSTALL_SCRIPT_PATH) -- $(INSTALL_ZIP_PATH) $(ADDON_NAME)

clean:
	rm -f $(INSTALL_ZIP_PATH)
