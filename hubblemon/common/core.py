
#
# Hubblemon - Yet another general purpose system monitor
#
# Copyright 2015 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os, sys, time, threading
import datetime

import common.settings
import binascii, socket
import data_loader.basic_loader
import data_loader.loader_factory


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
mod_cache = {}
mod_query_cache = {}

#
# default loader settings
#
local_storage_manager = data_loader.loader_factory.rrd_storage_manager(hubblemon_path)
#local_storage_manager = data_loader.loader_factory.sql_storage_manager(hubblemon_path)
#local_storage_manager = data_loader.loader_factory.tsdb_test_storage_manager(hubblemon_path)

remote_storage_manager = data_loader.loader_factory.remote_manager()

def loader(path, filter = None, title = ''):
	results = []

	info = _get_listener_info(path)
	
	if info[2] == 'local':
		try:
			param = info[1]
			handle = local_storage_manager.get_handle(param, path)
			return data_loader.basic_loader.basic_loader(handle, filter, title)
		except:
			return data_loader.basic_loader.basic_loader(None, [])
	else: # remote
		try:
			host, port = info[0].split(':')
			handle = remote_storage_manager.get_handle(host, int(port), path)
			return data_loader.basic_loader.basic_loader(handle, filter, title)
		except:
			return data_loader.basic_loader.basic_loader(None, [])
	

		


#
# data, system handling
#


def _get_listener_info(file):
	#print(file)
	name = file.split('/')[0]
	#ip = socket.gethostbyname(name)

	ret = binascii.crc32(bytes(name, 'utf-8'))
	n = len(common.settings.listener_list)
	idx = ret % n

	return common.settings.listener_list[idx]
	



# local or remote
def get_client_list():
	client_list = []

	for item in common.settings.listener_list:
		if item[2] == 'local':
			param = item[1]
			client_list += local_storage_manager.get_client_list(param)

		else: # remote
			address = item[0]
			host, port = address.split(':')
			port = int(port)
			handle = get_default_remote_handle(host, port)
			client_list += handle.get_client_list()

	return client_list

def get_data_of_client(client, prefix):
	info = _get_listener_info(client)
	data=""

	if info[2] == 'local':
		param = info[1]
		data= local_storage_manager.get_data_of_client(param, client, prefix)

	else: # remote
		address = info[0]
		host, port = address.split(':')
		port = int(port)
		handle = get_default_remote_handle(host, port)
		data= handle.get_data_of_client(client, prefix)

	return data



# local or remote
def get_data_list_of_client(client, prefix):
	info = _get_listener_info(client)
	data_list = []

	if info[2] == 'local':
		param = info[1]
		data_list += local_storage_manager.get_data_list_of_client(param, client, prefix)

	else: # remote
		address = info[0]
		host, port = address.split(':')
		port = int(port)
		handle = get_default_remote_handle(host, port)
		data_list += handle.get_data_list_of_client(client, prefix)

	return data_list
	

# local or remote
def get_all_data_list(prefix):
	data_list = []

	for item in common.settings.listener_list:
		if item[2] == 'local':
			base = item[1]
			data_list += local_storage_manager.get_all_data_list(base, prefix)
		else:
			address = item[0]
			host, port = address.split(':')
			port = int(port)
			handle = get_default_remote_handle(host, port)
			data_list += handle.get_all_data_list(prefix)


	return data_list


#
# plugins
#
def get_chart_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_chart_list(param)


def get_chart_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_chart_data(param)


def get_graph_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_graph_list(param)


def get_graph_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_graph_data(param)

def auth_fields(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	if type not in mod_query_cache:
		pkg = __import__('%s_mon.%s_query' % (type, type))
		mod = getattr(pkg, '%s_query' % type)
		mod_query_cache[type] = mod

	return mod_query_cache[type].auth_fields(param)


def query(param, ip):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	if type not in mod_query_cache:
		pkg = __import__('%s_mon.%s_query' % (type, type))
		mod = getattr(pkg, '%s_query' % type)
		mod_query_cache[type] = mod

	return mod_query_cache[type].query(param, ip)


def get_addon_page(param):
	if 'type' not in param:
		return ''

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_addon_page(param)




#
# functions that used for expr
#

import psutil_mon.psutil_view
import arcus_mon.arcus_view
import redis_mon.redis_view
import fnmatch


def system_view(client, item = 'brief', type='serial'):
	if isinstance(client, str):
		if '*' in client or '?' in client: # wild card
			clients = []
			all_clients = get_client_list()

			for c in all_clients:
				if fnmatch.fnmatch(c, client):
					clients.append(c)
		else:
			clients = [ client ]
	else: # list, tuple
		clients = client

	ret = []
	for client in clients:
		ret.append(psutil_mon.psutil_view.system_view(client, item))

	if type == 'merge':
		return data_loader.loader_factory.merge_loader(ret)

	return data_loader.loader_factory.serial_loader(ret)

def arcus_view(instance): # client/arcus_port
	if isinstance(instance, str):
		instances = [ instance ]
	else: # list, tuple
		instances = instance

	ret = []
	for instance in instances:
		ret.append(arcus_mon.arcus_view.arcus_view(instance))

	return data_loader.loader_factory.serial_loader(ret)


def arcus_instance_list(name):
	if isinstance(name, str):
		names = [ name ]
	else: # list, tuple
		names = name

	node_list = []
	for name in names:
		node_list += arcus_mon.arcus_view.arcus_cloud_map[name]

	return node_list



def arcus_cloud_list(zk = None):
	if zk == None:
		return list(arcus_mon.arcus_view.arcus_cloud_map.keys())
		
	if zk in arcus_mon.arcus_view.arcus_zk_map:
		return arcus_mon.arcus_view.arcus_zk_map[zk]

	return None





def for_each(name, filter, fun, start_ts = int(time.time())-60*30, end_ts = int(time.time())):

	# change to timestamp
	if isinstance(start_ts, str):
		start_date = datetime.datetime.strptime(start_ts, '%Y-%m-%d %H:%M')
		start_ts = int(start_date.timestamp())
	elif isinstance(start_ts, datetime.datetime):
		start_ts = int(start_ts.timestamp())
		
	if isinstance(end_ts, str):
		end_date = datetime.datetime.strptime(end_ts, '%Y-%m-%d %H:%M')
		end_ts = int(end_date.timestamp())
	elif isinstance(end_ts, datetime.datetime):
		send_ts = int(end_ts.timestamp())



	if isinstance(name, str):
		names = [ name ]
	else: # list, tuple
		names = name

	selected = []
	for name in names:
		ldr = loader(name)
		ldr.parse(start_ts, end_ts)
			
		if filter(ldr):
			selected.append(name)

	print('# selected: ' + str(selected))
	result = []
	for i in selected:
		ret = fun(i)
		if isinstance(ret, list):
			result += ret
		else:
			result.append(ret)

	#print(result)
	return result




	

#
# functions that used for query eval
# 

def return_as_string(result, p = {}):
	result = str(result)

	result = result.replace('\n', '<br>')
	result = result.replace(' ', '&nbsp')
	p['result'] = result
	return p['result']
	

def return_as_textarea(result, p = {}):
	p['result'] = '<textarea>%s</textarea>' % result
	return p['result']

def return_as_table(result, p = {}):
	tr = ''

	# cursor meta info 
	if hasattr(result, 'description'):
		td = ''
		for d in result.description:
			td += '<td>%s</td>' % d[0]
		tr += '<tr>%s</tr>' % td

	# values
	for row in result:
		td = ''
		for item in row:
			td += '<td>%s</td>' % item
		tr += '<tr>%s</tr>' % td

	p['result'] = '<table border="1">%s</table>' % tr
	return p['result']
			
		
	
	



# result zookeeper.load_all()
from arcus_mon.arcus_driver.arcus_util import zookeeper

def get_arcus_zk_load_all(addr):
	zoo = zookeeper(addr)
	zoo.load_all()
	return zoo

def get_arcus_zk_node_cloud_map(addr):
	arcus_node_cloud_map = {}

	zoo = zookeeper(addr)
	nodes = zoo.get_arcus_node_all()
	for node in nodes:
		arcus_node_cloud_map[node.ip + ":" + node.port] = node.code

	return arcus_node_cloud_map
	

	
	

