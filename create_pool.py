#!/usr/bin/env python
'''
----------------------------------------------------------------------------
 The contents of this file are subject to the "END USER LICENSE AGREEMENT FOR F5
 Software Development Kit for iControl"; you may not use this file except in
 compliance with the License. The License is included in the iControl
 Software Development Kit.

 Software distributed under the License is distributed on an "AS IS"
 basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
 the License for the specific language governing rights and limitations
 under the License.

 The Original Code is iControl Code and related documentation
 distributed by F5.

 The Initial Developer of the Original Code is F5 Networks,
 Inc. Seattle, WA, USA. Portions created by F5 are Copyright (C) 1996-2004 F5 Networks,
 Inc. All Rights Reserved.  iControl (TM) is a registered trademark of F5 Networks, Inc.

 Alternatively, the contents of this file may be used under the terms
 of the GNU General Public License (the "GPL"), in which case the
 provisions of GPL are applicable instead of those above.  If you wish
 to allow use of your version of this file only under the terms of the
 GPL and not to allow others to use your version of this file under the
 License, indicate your decision by deleting the provisions above and
 replace them with the notice and other provisions required by the GPL.
 If you do not delete the provisions above, a recipient may use your
 version of this file under either the License or the GPL.
----------------------------------------------------------------------------
'''

def create_pool(obj,pool, lbmethod, pl_mems):
	pool = '/Common/%s' % pool
	pmlist = []
	for x in pl_mems.split(','):
		pm = {}
		y = x.split(':')
		pm['address'] = str(y[0])
		pm['port'] = int(y[1])
		pmlist.append(pm)
		
	try:
		pllist = obj.LocalLB.Pool.get_list()
		if pool in pllist:
			obj.LocalLB.Pool.add_member_v2([pool], [pmlist])

		else:
			obj.LocalLB.Pool.create_v2([pool],[lbmethod],[pmlist])

		return obj.LocalLB.Pool.get_member_v2([pool])
	except Exception, e:
		print e


if __name__ == "__main__":

	import bigsuds
	import getpass
	import sys

	# Directory location of bigsuds.py file
	sys.path.append(r'C:\dev')

	if len(sys.argv) < 6:
		print "\n\n\tUsage %s ip_address username poolname lbmethod memberlist" % sys.argv[0]
		sys.exit()

	a = sys.argv[1:]

	print "\nHey %s, please enter your password below.\n" % a[1]
	upass = getpass.getpass()

	try:   
		b = bigsuds.BIGIP(
			hostname = a[0], 
			username = a[1], 
			password = upass,
			)
	except Exception, e:
		print e

	poolinfo = create_pool(b, a[2], a[3], a[4])
	for x in poolinfo:
		print "Pool: %s" % a[2]
		for y in x:
			print "\t%s:%d" % (y['address'], y['port'])

