
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



import os, socket, sys, time, copy, datetime, threading
import data_loader

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import arcus_mon
import common.settings
import common.core
import kazoo


arcus_preset = [['bytes', 'total_malloced', 'engine_maxbytes'], 'curr_items', (lambda x: x['get_hits'] / x['cmd_get'] * 100, 'hit_ratio'), ['cmd_get', 'cmd_set'], 'cmd_get', 'cmd_set', 'evictions', 'reclaimed', ['bytes_read', 'bytes_written'], ['rusage_user', 'rusage_system'], 'curr_connections', ['cmd_lop_create', 'cmd_lop_insert', 'cmd_lop_get', 'cmd_lop_delete'], ['cmd_sop_create', 'cmd_sop_delete'], ['cmd_sop_insert', 'cmd_sop_get', 'cmd_sop_exist'], ['cmd_bop_create', 'cmd_bop_delete'], ['cmd_bop_insert', 'cmd_bop_update', 'cmd_bop_incr', 'cmd_bop_decr'], ['cmd_bop_get', 'bop_get_ehits', 'bop_get_nhits'], ['cmd_bop_count', 'cmd_bop_mget', 'cmd_bop_smget'], ['getattr_hits', 'setattr_hits'], ['cmd_flush', 'cmd_flush_prefix'], ['hb_count', 'hb_latency'], ['sticky_bytes', 'sticky_limit'], ['incr_hits', 'decr_hits']]


def arcus_view(path, title = ''):
	return common.core.loader(path, arcus_preset, title)

arcus_prefix_preset = [ ['cmd_get', 'cmd_hit', 'cmd_set', 'cmd_del'],
			['cmd_lop_create', 'cmd_lop_insert', 'lop_insert_hits', 'cmd_lop_delete', 'lop_delete_hits', 'cmd_lop_get', 'lop_get_hits'],
			['cmd_sop_create', 'cmd_sop_insert', 'sop_insert_hits', 'cmd_sop_delete', 'sop_delete_hits', 'cmd_sop_get', 'sop_get_hits'],
			['cmd_bop_create', 'cmd_bop_insert', 'bop_insert_hits', 'cmd_bop_delete', 'bop_delete_hits', 'cmd_bop_get', 'bop_get_hits']]




#
# chart list
#
arcus_cloud_map = {}
arcus_cloud_list_map = {} # for arcus_cloud_list page
arcus_zk_map = {} 
last_ts = 0


def _zk_load(addr, cloud_map, cloud_list_map, zk_map):
	print('# zookeeper %s load' % addr)
	try:
		zoo = common.core.get_arcus_zk_load_all(addr)
	except Exception as e:
		print('[ERROR] kazoo exception: %s' % addr)
		print(e)
		return
		

	zk_map[addr] = list(zoo.arcus_cache_map.keys())
	for code, cache in zoo.arcus_cache_map.items():
		node_list = cache.node
		node_str_list = []

		for node in node_list:
			name = node.name
			if name == '':
				try:
					name = socket.gethostbyaddr(node.ip)[0]
					name_list = name.split('.')
					if len(name_list) > 2:
						del name_list[-1]
						del name_list[-1] # remove nhncorp.com

						name = ''
						for n in name_list:
							name += n
							name += '.'


						name = name[:-1] # remove last .
					
				except Exception as e:
					name = node.ip

			node_str = '%s/arcus_%s' % (name, node.port)
			node_str_list.append(node_str)

		node_str_list.sort()
		cloud_list_map[code] = [addr, node_str_list[:], zoo.arcus_cache_map[code].meta]

		cloud_map[code] = node_str_list
		cloud_map[code].sort()

	print('# zookeeper %s load done' % addr)


def init_plugin():
	global arcus_cloud_map
	global arcus_cloud_list_map
	global arcus_zk_map
	global last_ts

	ts = time.time()
	if ts - last_ts < 600:
		return
	last_ts = ts

	print('#### cloud init ########')

	arcus_cloud_map_tmp = {}
	arcus_cloud_list_map_tmp = {}
	arcus_zk_map_tmp = {}

	threads = []
	#for addr in ['gasan.arcuscloud.nhncorp.com:17288']:
	for addr in common.settings.arcus_zk_addrs:
		th = threading.Thread(target = _zk_load, args = (addr, arcus_cloud_map_tmp, arcus_cloud_list_map_tmp, arcus_zk_map_tmp))
		th.start()
		threads.append(th)

	for th in threads:
		th.join()
		

	arcus_cloud_map = arcus_cloud_map_tmp
	arcus_cloud_list_map = arcus_cloud_list_map_tmp
	arcus_zk_map = arcus_zk_map_tmp
	print (arcus_cloud_map)
	


def get_chart_data(param):
	#print(param)
	global arcus_cloud_map


	type = 'arcus_stat'
	if 'type' in param:
		type = param['type']

	if 'cloud' not in param or 'instance' not in param:
		return None

	cloud_name = param['cloud']
	instance_name = param['instance']

	if cloud_name not in arcus_cloud_map and cloud_name != '[SUM]':
		return None

	if type == 'arcus_stat':
		if instance_name == '[SUM]':
			loader_list = []
			for node in arcus_cloud_map[cloud_name]:
				if node.startswith('['):
					continue # skip

				loader = common.core.loader(node, arcus_preset, title=node)
				loader_list.append(loader)

			results = data_loader.loader_factory.sum_all(loader_list)
			
		elif instance_name == '[EACH]':
			loader_list = []
			for node in arcus_cloud_map[cloud_name]:
				if node.startswith('['):
					continue # skip

				loader = common.core.loader(node, arcus_preset, title=node)
				loader_list.append(loader)

			results = data_loader.loader_factory.merge(loader_list)

		else:
			for node in arcus_cloud_map[cloud_name]:
				if node.startswith(instance_name):
					results = common.core.loader(node, arcus_preset, title=node)
					break

	elif type == 'arcus_prefix':
		if 'prefix' not in param:
			return None

		prefix = param['prefix']
		port = os.path.basename(instance_name)
		instance = os.path.dirname(instance_name)

		if prefix == '[ALL]':
			results = []
			client, port = instance_name.split('/')
			file_list = common.core.get_data_list_of_client(client, port + '-')

			for file in file_list:
				file_path = os.path.join(instance, file)

				tmp_port, prefix_name = file.split('-', 1)
				curr_prefix, dummy = prefix_name.split('.rrd')
				results.append(common.core.loader(file_path, arcus_prefix_preset, curr_prefix)) # all lists

			results = data_loader.loader_factory.serial(results)
		else:
			path = os.path.join(instance, '%s-%s' % (port, prefix))
			results = common.core.loader(path, arcus_prefix_preset, title=prefix)
		
	return results


def get_chart_list(param):
	print(param)

	type = 'arcus_stat'
	if 'type' in param:
		type = param['type']

	cloud = ''
	instance = ''

	if 'cloud' in param:
		cloud = param['cloud']

	if 'instance' in param:
		instance = param['instance']

	if type == 'arcus_stat':
		if cloud == '':
			return (['cloud', 'instance'], arcus_cloud_map)
		else:
			str_list = copy.copy(arcus_cloud_map[cloud])
			str_list.insert(0, '[SUM]')
			str_list.insert(0, '[EACH]')
			return (['cloud', 'instance'], {cloud:str_list})

	elif type == 'arcus_query':
		if cloud == '':
			return (['cloud', 'instance'], arcus_cloud_map)
		else:
			str_list = copy.copy(arcus_cloud_map[cloud])
			str_list.insert(0, '[ALL]')
			return (['cloud', 'instance'], {cloud:str_list})


	elif type == 'arcus_prefix':
		if cloud == '' or instance == '':
			return (['cloud', 'instance', 'prefix'], arcus_cloud_map)

		client, port = instance.split('/')

		file_list = common.core.get_data_list_of_client(client, port + '-')

		prefix_list = ['[ALL]']

		for file in file_list:
			port, prefix_name = file.split('-', 1)
			prefix, dummy = prefix_name.split('.rrd')
			prefix_list.append(prefix)
		
		prefix_map = {}
		prefix_map[cloud] = { instance:prefix_list }

		return (['cloud', 'instance', 'prefix'], prefix_map)

	return (['cloud', 'instance'], arcus_cloud_map)


def get_graph_list(param):
	#print(param)
	ret = {}
	for zk in common.settings.arcus_zk_addrs:
		ret[zk] = True

	return (['zk'], ret)

	
def get_graph_data(param):
	#print(param)
	zk = param['zk']
	zoo = common.core.get_arcus_zk_load_all(zk)

	# TODO: enable multi graph modify
	# modify description if needed
	for k, v in param.items():
		#print(k, v)
		if k.startswith('desc_'):
			cloud = k.split('_', 1)[1]
			
			path = '/arcus/meta/%s' % cloud
			print('**** %s, %s, %s' % (k, cloud, path))

			if zoo.zk_exists(path):
				zoo.zk_update(path, v)
			else:
				zoo.zk_create(path, v)

			if cloud in zoo.arcus_cache_map:
				zoo.arcus_cache_map[cloud].meta[0] = v
			if cloud == 'zookeeper':
				zoo.meta[0] = v

	# make graph data
	results = []
	graph_data = render_arcus_graph(zoo, param)
	return graph_data




import time, socket
from graph.node import graph_pool

def set_description(zoo, param):
	result = ''

	if 'admin' in param:
		#%s:<br><input type="text" name="desc_%s" value="%s">
		template = """
			<form class='desc_input' action='.'>
				%s:<br><textarea rows="4" cols="40" textalign="left"
					 name="desc_%s">%s</textarea>
				<input type="submit" value="submit">
				<input type="hidden" name="zk" value="%s">
				<input type="hidden" name="admin" value="">
				<input type="hidden" name="type" value="arcus_graph">
			</form>
			<br>
		"""

		result = template % ('zookeeper', 'zookeeper', zoo.meta[0], zoo.address)

		for code, cache in sorted(zoo.arcus_cache_map.items()):
			result += template % (code, code, cache.meta[0], zoo.address)

	else:
		template = """
			<div class='desc_title'>
			%s:
			</div>
			<div class='desc_value'>
			<textarea rows="4" cols="40" textalign="left">%s</textarea>
			</div>
			<br>
		"""

		result = template % ('zookeeper', zoo.meta[0])

		for code, cache in sorted(zoo.arcus_cache_map.items()):
			result += template % (code, cache.meta[0])

	return result

def render_arcus_graph(zoo, param):
	ts_start = time.time()

	position = 20 # yaxis
	pool = graph_pool(position)

	node_zk = pool.get_node(zoo.address)
	node_zk.weight = 300
	node_zk.color = '0000FF'

	for code, cache in zoo.arcus_cache_map.items():
		node_cache = pool.get_node(code)
		node_cache.weight = 200
		node_cache.color = '00FF00'
		node_cache.link(node_zk)
		
	for code, cache in zoo.arcus_cache_map.items():
		node_cache = pool.get_node(code)

		for node in cache.active_node:
			try:
				hostname, aliaslist, ipaddr = socket.gethostbyaddr(node.ip)
				ret = hostname.split('.')
				if len(ret) > 2:
					hostname = '%s.%s' % (ret[0], ret[1])
					
			except socket.herror:
				hostname = node.ip

			node_node = pool.get_node(hostname)
			node_node.weight = 100
			node_node.color = '00FFFF'

			if node.noport:
				node_node.link(node_cache, node.port, 'FF0000')
			else:
				node_node.link(node_cache, node.port, '00FF00')

		for node in cache.dead_node:
			try:
				hostname, aliaslist, ipaddr = socket.gethostbyaddr(node.ip)
				ret = hostname.split('.')
				if len(ret) > 2:
					hostname = '%s.%s' % (ret[0], ret[1])
			except socket.herror:
				hostname = node.ip

			node_node = pool.get_node(hostname)
			node_node.weight = 100
			node_node.color = '303030'

			node_node.link(node_cache, node.port, 'EEEEEE')

	# set meta info
	pool.description = set_description(zoo, param)
	result = pool.render()

	ts_end = time.time()
	print('## %s elapsed: %f' % (zoo.address, ts_end - ts_start))
	return result


def get_addon_page(param):
	print(param)

	if 'type' not in param:
		return ''

	if param['type'] == 'arcus_list':
		return get_arcus_cloud_page(param)
	elif param['type'] == 'arcus_util':
		return get_arcus_util_page(param)

	return ''
	

def get_arcus_cloud_page(param):
	if 'zk' in param:
		# modify description if needed
		zk = param['zk']
		zoo = common.core.get_arcus_zk_load_all(zk)

		for k, v in param.items():
			#print(k, v)
			if k.startswith('desc_'):
				cloud = k.split('_', 1)[1]

				path = '/arcus/meta/%s' % cloud
				#print('**** %s, %s, %s' % (k, cloud, path))

				if zoo.zk_exists(path):
					zoo.zk_update(path, v)
				else:
					zoo.zk_create(path, v)

				if cloud in zoo.arcus_cache_map:
					zoo.arcus_cache_map[cloud].meta = [v, None]
					arcus_mon.arcus_view.arcus_cloud_list_map[cloud][2] = [v, None] # [zk, instance list, meta]
				if cloud == 'zookeeper':
					zoo.meta = [v, None]



	cloud_list = ''
	color = '#EEEEFF'

	idx = 1 
	for cloud_name, v in sorted(arcus_mon.arcus_view.arcus_cloud_list_map.items()):
		zookeeper = v[0]
		node_str_list = v[1]
		meta = v[2]
		
		if color == '#EEEEFF':
			color = '#EEFFEE'
		else:
			color = '#EEEEFF'

		tmp ="""<div style="float:left; width:3%%;">%d</div>
			<div style="float:left; width:12%%;"><a href="/chart?type=arcus_stat&cloud=%s&instance=[EACH]">%s</a></div>
			<div style="float:left; width:25%%;"><a href="/graph?type=arcus_graph&zk=%s">%s</a></div>
			""" % (idx, cloud_name, cloud_name, zookeeper, zookeeper)
		idx += 1

		tmp_instance = ''
		for node in v[1]:
			tmp_instance +="""<div><a href="/chart?type=arcus_stat&cloud=%s&instance=%s">%s</a></div>""" % (cloud_name, node, node)


		tmp_instance += "<div><b>total instances: %d</b></div>" % len(node_str_list)
		

		tmp += '<div style="float:left; width:20%%;">%s</div>' % (tmp_instance)

		mtime = ''
		if isinstance(meta, list) and hasattr(meta[1], 'mtime'):
			mtime = str(datetime.datetime.fromtimestamp(int(meta[1].mtime)/1000))

		if 'admin' in param:
			tmp += '''<div style="float:left; width:40%%;">
				<form class='desc_input' action='.'>
					<textarea rows="%d" textalign="left" style="width:100%%;" name="desc_%s">%s</textarea>
					<input type="submit" value="submit">
					<input type="hidden" name="zk" value="%s">
					<input type="hidden" name="admin" value="">
					<input type="hidden" name="type" value="arcus_list">
				</form>
				<div>
				%s
				</div>
				</div>''' % (len(node_str_list) + 3, cloud_name, str(meta[0]), zookeeper, mtime)
		else:
			tmp += '''<div style="float:left; width:40%%;">
				<textarea rows="%d" textalign="left" style="width:100%%;">%s</textarea>
				<div>
				%s
				</div>
				</div>''' % (len(node_str_list) + 3, str(meta[0]), mtime)


		cloud_list += '<div style="width:100%%; background:%s;">%s</div><div style="clear:both;"></div><div>&nbsp</div>' % (color, tmp)
		
		
	return cloud_list



arcus_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arcus_driver')
sys.path.append(arcus_driver_path)
from arcus_mon.arcus_driver.arcus import *
from arcus_mon.arcus_driver.arcus_mc_node import *

def get_arcus_util_page(param):

	zk = ''
	cloud = ''
	key = ''
	result = ''
	value = ''
	exp_time = ''

	if 'zk' in param and 'cloud' in param and 'key' in param:
		zk = param['zk']
		cloud = param['cloud']
		key = param['key']
		

		if zk != '' and cloud != '' and key != '':
			conn = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
			conn.connect(zk, cloud)

			if 'set' in param:
				value = param['value']
				etime = param['exp_time']

				if value == '': # prevent miss click
					result = 'empty value'
				else:
					if etime.isdigit():
						etime = int(etime)
					else:
						etime = 0

					ret = conn.set(key, value, etime)
					result = ret.get_result()

			elif 'get' in param:
				ret = conn.get(key)
				result = ret.get_result()
				if result is None:
					result = 'Not Found'


			conn.disconnect()

	util_page = '''
		<div>
		<form action='.'>
			zookeeper (ex: gasan.arcuscloud.nhncorp.com:17288)
			<br>
			<input id="id_zk" name="zk" type="text" value="%s"/>
			<br>
			cloud (ex: apigw)
			<br>
			<input id="id_cloud" name="cloud" type="text" value="%s"/>
			<br>
			key
			<br>
			<input id="id_key" name="key" type="text" value="%s"/>
			<input type="submit" name="get" value="get">
			<br>
			value
			<br>
			<input id="id_value" name="value" type="text" value="%s"/>
			<br>
			expire time (default: 0)
			<br>
			<input id="id_expiretime" name="exp_time" type="text" value="%s"/>
			<input type="submit" name="set" value="set">
			<input type="hidden" name="type" value="arcus_util">
		</form>
		</div>
		<br><br>
		<div>
		%s
		</div>
		''' % (zk, cloud, key, value, exp_time, result)
		
	return util_page



