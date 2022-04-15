/*

    getCamNamePort.cpp:
        pPint cameras' names with their accosiated USB ports' name
    
    Notes:    
        Ms.Jesscia Baron manually bound the cameras with USB ports.
        So this code autodetect cameras with their USB port names.

    Compile & run:
        1. Uncomment src/getCamNamePort.cpp in the add_executable() in fileCMakeLists.txt
        2. Go to build/ and type:
            - cmake ../
            - make clean
            - make
        3. in the build/, run ./camera

*/


#include <iostream>
#include <stdlib.h>

#include <gphoto2/gphoto2.h>

#include "samples.h"




int main()
{
    Camera      *camera;
    int         ret, count, i;
    GPContext   *context;


    context = sample_create_context();
    
    /*
        camear name and camera USB port can be get from src/getCamNamePort.cpp
    */
    ret = sample_open_camera (&camera, "Canon EOS 5DS R", "usb:001,001", context);
    if (ret < GP_OK) fprintf(stderr,"Camera %s on port %s failed to open\n", "Canon EOS 5DS R", "usb:001,001");


    FILE 	*f;
	char	*data;
	unsigned long size;
    int	retval;

    capture_to_memory(camera, context, (const char**)&data, &size);

    f = fopen("foo2.cr2", "wb");
	if (f) {
		retval = fwrite (data, size, 1, f);
		if (retval != (int)size) {
			printf("  fwrite size %ld, written %d\n", size, retval);
		}
		fclose(f);
	} else
		printf("  fopen foo2.jpg failed.\n");

    gp_camera_exit(camera, context);

    return 0;
}
