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
    CameraList	*list;
    Camera      **cams;
    int         ret, count, i;
    const char  *name, *value;
    GPContext   *context;


    context = sample_create_context();
    

    ret = gp_list_new (&list);
    count = sample_autodetect (list, context);
	if (count < GP_OK) 
    {
		printf("No cameras detected.\n");
		return 1;
	}

	/* Now open all cameras we autodected for usage */
	printf("Number of cameras: %d\n", count);
	cams = (Camera **)calloc (sizeof (Camera),count);
    for (i = 0; i < count; i++) 
    {
        gp_list_get_name  (list, i, &name);
        gp_list_get_value (list, i, &value);
        printf("%s --- %s\n", name, value);
        ret = sample_open_camera (&cams[i], name, value, context);
        if (ret < GP_OK) fprintf(stderr,"Camera %s on port %s failed to open\n", name, value);
    }
    return 0;
}
