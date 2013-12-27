from RPi import GPIO
import time
import subprocess

enabled = False

def enableAccessPoint():
  global enabled
  if enabled:
    print "already enabled"
    return
  enabled = True
  print "enabling access point..."
  subprocess.call(['/sbin/ifdown', 'wlan0'])
  subprocess.call(['/sbin/ifconfig', 'wlan0', '192.168.99.1'])
  subprocess.call(['/usr/sbin/hostapd', '-B', '/etc/hostapd/hostapd.conf', '-P', '/home/pi/hostapd.pid'])
  subprocess.call(['/usr/sbin/service', 'isc-dhcp-server', 'start'])

def disableAccessPoint():
  global enabled
  if not enabled:
    print "already disabled"
    return
  enabled = False
  print "disabling access point..."
  subprocess.call(['/usr/sbin/service', 'isc-dhcp-server', 'stop'])
  f = open('/home/pi/hostapd.pid', 'r')
  pid = f.readline().rstrip('\n')
  f.close()
  subprocess.call(['/bin/kill', pid])
  subprocess.call(['/sbin/ifconfig', 'wlan0', 'down'])
  subprocess.call(['/sbin/ifup', 'wlan0'])

def switch(channel):
  if GPIO.input(channel):
    enableAccessPoint()
  else:
    disableAccessPoint();

if __name__ == '__main__':
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
  if (GPIO.input(4)): enableAccessPoint()

  GPIO.add_event_detect(4, GPIO.BOTH, callback = switch)
  while True: time.sleep(1)
