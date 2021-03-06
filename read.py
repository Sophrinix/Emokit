import time
import pywinusb.hid as hid

from aes import rijndael

key = '\x31\x00\x35\x54\x38\x10\x37\x42\x31\x00\x35\x48\x38\x00\x37\x50'
rijn = rijndael(key, 16)

iv = [0]*16
def decrypt(data):
	global iv
	dec = list(map(ord, rijn.decrypt(data[:16])))
	dec2 = list(map(ord, rijn.decrypt(data[16:])))
	data = list(map(ord, data))
	#dec2 = [data[i] ^ dec2[i] for i in range(16)]
	#dec = (dec[i] ^ iv[i] for i in range(16))
	#iv = map(ord, data[16:])
	return ''.join(map(chr, dec + dec2))

count = 0
def sample_handler(data):
	global count
	assert data[0] == 0
	data = ''.join(map(chr, data[1:]))
	print ' '.join('%02x' % ord(c) for c in decrypt(data))
	count += 1

def main(fn=None):
	if fn == None:
		for device in hid.find_all_hid_devices():
			if device.vendor_id == 0x21A1 and device.product_name == 'Brain Waves':
				try:
					device.open()
					device.set_raw_data_handler(sample_handler)
					while device.is_plugged() and count < 1000:
						time.sleep(0.1)
				finally:
					device.close()
					break
	else:
		for line in file(fn, 'r').readlines():
			data = [0] + [int(x, 16) for x in line.strip().split(' ')]
			sample_handler(data)

if __name__=='__main__':
	import sys
	main(*sys.argv[1:])
