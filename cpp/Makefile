#
TARGET = de1_demo

#
ALT_DEVICE_FAMILY ?= soc_cv_av
SOCEDS_ROOT ?= $(SOCEDS_DEST_ROOT)
HWLIBS_ROOT = $(SOCEDS_ROOT)/ip/altera/hps/altera_hps/hwlib
CROSS_COMPILE = arm-linux-gnueabihf-
CFLAGS = -g -Wall   -D$(ALT_DEVICE_FAMILY) -I$(HWLIBS_ROOT)/include/$(ALT_DEVICE_FAMILY)   -I$(HWLIBS_ROOT)/include/ -std=c++11 
LDFLAGS =  -g -Wall 
CC = $(CROSS_COMPILE)g++
ARCH= arm

build: $(TARGET)
$(TARGET): de1_demo.o 
	$(CC) $(LDFLAGS)   $^ -o $@	
%.o : %.cpp
	$(CC) $(CFLAGS) -c $< -o $@
#%.so : %.cpp
#	$(CC) $(LDFLAGS)   $^ -fPIC -shared -o $@

.PHONY: clean
clean:
	rm -f $(TARGET) *.a *.o *~ 
