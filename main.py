#coding: utf-8

import os
import subprocess
import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from csvtotable import convert

minute = ['30m', '60m']
st = ["SH000001", "SZ399001", "SH000016", "SH000905"]

headers = {
	"cookie": "Hm_lvt_1db88642e346389874251b5a1eded6e3=1641263131; device_id=29d774b80d9a46b821260a854f02d63d; s=cm176xbuuh; xq_is_login=1; acw_tc=3ccdc14b16417787339238821e5ef130d8f01529d9dd1615e65684695ede83; xqat=e7e953840874f253be2ab10f1add80915f6571ea; xq_a_token=e7e953840874f253be2ab10f1add80915f6571ea; xq_r_token=9f29afbe70938db9b29cfb87f985bfe5419d6390; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGcmsmc_platform_user_info_updateiOiJSUzI1NiJ9.eyJ1aWQiOjYxNTg4NTA2MDQsImlzcyI6InVjIiwiZXhwIjoxNjQ0MzcwNzMzLCJjdG0iOjE2NDE3Nzg3MzM5NDUsImNpZCI6ImQ5ZDBuNEFadXAifQ.AvkYbhKRlacAgxQdixgxG37aXPhAGqzoZVBNvRgez7PaN9_Ftt3pPH-84_vJWpSBFNa5yCxheT2toQ8DJiENY9n8bhrWowQn7ZG_AZD8ZrTIBfifSIooTAoI_6FvQJ9UulWjG3WVaoQ490gFLBzd3Hhdp8taFiowIhmf1VTeZHpshNxmFgyliEOV8eNz0AjVVXd2BNTuobTcfuwwKS39A8zqqYb0gGaklkXIUPC42c2Ukvmeiue21VnvbPgPWU1MLnpkFaURcYEZ-pA7S78x5V-lTXvLTXm96ad8C56GnZqwWQRl73nCM-OW_p5xPFk09QabKLVJ6DXJnlBg3ekk6A; is_overseas=0; u=881641778736136; cookiesu=881641778736136; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1641778736",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}


def makeJson(stdata):
	res = {}
	for line in stdata:
		volume = str(line[1])
		chg = str(line[6])
		percent = str(line[7])
		amount = str(int(line[9]))
		datetimej = (time.strftime("%Y%m%d,%H%M", time.localtime(int(line[0])/1000)))
		stdate, sttime = datetimej.split(',')
		# print(stdate,sttime)

		if not stdate in res.keys():
			res[stdate] = {}

		res[stdate][sttime] = volume+',' +percent+ ','+chg

	return res

def getYesday(date):
	'''
	Mon to next Fri
	'''

	if date.strftime("%a") == 'Mon':
		return (date + timedelta(days=-3)).strftime("%Y%m%d")
	else:
		return (date + timedelta(days=-1)).strftime("%Y%m%d")

def makeCsv(st_dict, csv_file):
	yes_list = []
	for k in list(st_dict.keys()):
		yes_list.append(st_dict[k].keys())

	l_key = yes_list[2]       ## 取第二个值的1000、1030 这些值

	fd = open("./tmp.csv", 'w')

	for stdate in list(st_dict.keys()):
		dt = datetime.strptime(stdate, "%Y%m%d")
		yesday = getYesday(dt)

		if yesday not in st_dict.keys() or len(st_dict[yesday]) != len(l_key):
			st_dict[yesday] = {}

			for k in l_key:
				st_dict[yesday][k] = 1

		for k,v in st_dict[stdate].items():
			volume, percent, chg = v.split(',')
			yes_volume = str(st_dict[yesday][k]).split(',')[0]
			# print(stdate, k, (str(round(int(volume)/int(yes_volume), 8))), chg,str(percent))
			
			res_str = (','.join([stdate, k, (str(round(int(volume)/int(yes_volume), 8))), chg,str(percent)+'\n']))
			fd.write(res_str)

	fd.close()

	# 排序后也不能正常显示
	ce = pd.read_csv("./tmp.csv", index_col = False, names=['date', 'time', 'p', 'chg', 'percent'], skiprows=16)
	data = ce.sort_values(by='date', ascending=False)
	data.to_csv(csv_file, mode='w', index=False, header=False)
	os.remove("./tmp.csv")

for n_min in minute:
	for name in st:
		kurl_60 = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=%s&begin=%d&period=%s&type=before&count=-64&indicator=kline" % (name, int(time.time()*1000), n_min)
		res = requests.get(kurl_60, headers=headers).json()
		res_list = res['data']['item']

		if not os.path.exists("./html"):
			os.makedirs("./html")

		if not os.path.exists("./csv"):
			os.makedirs("./csv")

		csv_file = "./csv/%s-%s.csv" % (name,n_min)
		html_file = "./html/%s-%s.html" % (name, n_min)

		makeCsv(makeJson(res_list), csv_file)
		cmd = "/opt/pb/py3/bin/csvtotable -nh -o %s %s" % (csv_file, html_file)
		print(cmd.split())
		subprocess.Popen(cmd.split())


