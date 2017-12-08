/*
 * Copyright 2010-2014, 2017 Pawel Daniluk
 * 
 * This file is part of PyDesc.
 * 
 * PyDesc is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * PyDesc is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with PyDesc.  If not, see <http://www.gnu.org/licenses/>.
 */
 


#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<unistd.h>

#ifdef  __APPLE__
#include<mach/mach.h>
#else
#include<sys/sysinfo.h>
#endif


#include"simple_macros.h"
#include"arrays.h"

#ifdef  __APPLE__
void do_host_statistics(host_name_port_t host, host_flavor_t flavor, host_info_t info, mach_msg_type_number_t *count)
{
    kern_return_t kr;

    kr = host_statistics(host, flavor, (host_info_t)info, count);
    if (kr != KERN_SUCCESS) {
        (void)mach_port_deallocate(mach_task_self(), host);
        mach_error("host_info:", kr);
        abort();
    }
}
#endif

int memory_available(size_t size, float frac)
{
	int page_size;
	long int avpages;

#ifdef  __APPLE__
    vm_size_t tmp_page_size;
    vm_statistics_data_t vm_stat;
    mach_msg_type_number_t count = HOST_VM_INFO_COUNT;
    host_name_port_t host = mach_host_self();

    host_page_size(host, &tmp_page_size);
    do_host_statistics(host, HOST_VM_INFO, (host_info_t)&vm_stat, &count);

	page_size=tmp_page_size;

	avpages=vm_stat.free_count+vm_stat.inactive_count;

//	P_INT(page_size); P_INT((int)avpages); P_INT(page_size*avpages); P_NL;
#else
	page_size=getpagesize();
	avpages=get_avphys_pages();
#endif

	long int req_pages=size/page_size;

	if((float)req_pages/(float)avpages<=frac) return 1;

	return 0;
}

size_t array_size(long int n, long int m, long int size)
{
	size_t res=sizeof(void *)*n+size*n*m;

	return res;
}

void **array_alloc(long int n, long int m, long int size)
{
    /*
     * CAVEAT EMPTOR: This is a terribly ugly hack.
     *
     * rres is moved forward by 3 cells to provide room in which to hide an array size.
     *
     * This has to be taken into account when destroying the array or perfoming non-standard operations.
     *
     */


	void **rres=calloc(MAX(n,1)+3, sizeof(void*));

	if(!rres && n) {
		printf("alloc error: %ld\n", (long int)sizeof(void*)*n);
		return 0;
	}

    rres+=3;

    rres[-3]=(void *)n;
    rres[-2]=(void *)m;
    rres[-1]=(void *)size;


	rres[0]=calloc(n*m, size);

	if(!rres[0]) {
		printf("alloc error: %ld\n", (long int)size*n*m);
		free(rres-3);
		return 0;
	}

	for(int i=1; i<n; i++) rres[i]=rres[i-1]+m*size;

	return rres;
}

void **array_realloc(void **arr, long int n, long int m, long int size)
{
    long int oldn=(long int)arr[-3];
    long int oldm=(long int)arr[-2];
    long int oldsize=(long int)arr[-1];

    if(oldm!=m || oldsize!=size) {
        printf("array_realloc: Changing of second dimension or cell size not implemented yet.\n");
        abort();
    }

    void **rres=realloc(arr-3, (n+3)*sizeof(void *));

	if(!rres || !n) {
		printf("alloc error: %ld\n", (long int)sizeof(void*)*n);
		return 0;
	}

    rres+=3;

    rres[-3]=(void *)n;
    rres[-2]=(void *)m;
    rres[-1]=(void *)size;

	rres[0]=realloc(rres[0], n*m*size);

	if(!rres[0]) {
		printf("alloc error: %ld\n", (long int)size*n*m);
		free(rres);
		return 0;
	}

	for(int i=1; i<n; i++) rres[i]=rres[i-1]+m*size;

    if(oldn<n) {
        memset(rres[oldn], 0, (n-oldn)*m*size);
    }

    return rres;
}

void array_set(void **arr, int val)
{
    long int n=(long int)arr[-3];
    long int m=(long int)arr[-2];
    long int size=(long int)arr[-1];

	memset(arr[0], val, size*n*m);
}


void array_cpy(void **dst, void **src)
{
    long int dn=(long int)dst[-3];
    long int dm=(long int)dst[-2];
    long int dsize=(long int)dst[-1];
    long int sn=(long int)src[-3];
    long int sm=(long int)src[-2];
    long int ssize=(long int)src[-1];

    if(dn!=sn || dm!=sm || dsize!=ssize) {
        printf("array_cpy: array sizes differ: %ld %ld %ld != %ld %ld %ld\n", dn, dm, dsize, sn, sm, ssize);
    }

	memcpy(dst[0], src[0], dsize*dn*dm);
}

void array_free(void **array)
{
	free(array[0]);
	free(array-3); // The pointer has been moved forward in array_alloc.
}


