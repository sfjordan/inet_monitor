#!/usr/bin/python3.4
import os, sys, csv, time, logging, subprocess, traceback
import datetime as DT
from matplotlib.dates import date2num
import matplotlib.pyplot as plt

LOG_FILE = "/home/sfjordan/network_speed/speed_data.log"

SPEED_CSV_FILE = "/home/sfjordan/network_speed/speed_data.csv"
SPEED_IMG_FILE = SPEED_CSV_FILE[:-3]+"png"

PKTLOSS_CSV_FILE = "/home/sfjordan/network_speed/pktloss_data.csv"
PKTLOSS_IMG_FILE = PKTLOSS_CSV_FILE[:-3]+"png"

LAT_CSV_FILE = "/home/sfjordan/network_speed/lat_data.csv"
LAT_IMG_FILE = LAT_CSV_FILE[:-3]+"png"

TIME_FMT_WRITE = "%Y-%m-%d %H:%M:%S"
TIME_FMT_DISPLAY = "%x %I:%M %p"

IPERF_SERV = "iperf.scottlinux.com"
RETRY_WAIT_SECONDS = 30
RETRY_ATTEMPTS = 20

GOOGLE_DNS_V6 = "2001:4860:4860::8888"
PING_COUNT = 100

def cmd_retry(cmd_list):
  try:
    for attempt in range(RETRY_ATTEMPTS):
      try:
        res = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = res.communicate()

        # check for errors
        if res.poll() or not output:
          raise subprocess.CalledProcessError(
              res.poll(),
              cmd_list,
              error.decode().strip()
          )
        else:
          return output, ""
      except subprocess.CalledProcessError as e:
        logging.error(
            "command {} failed [ERR: {}], reporting: {}".format(
              e.cmd, e.returncode, e.output
            )
        )
        logging.error("Failed on attempt {}".format(attempt+1))
        time.sleep(RETRY_WAIT_SECONDS)
    else:
      logging.critical("All attempts at command {} failed!".format(cmd_list))
      return "", "All attempts failed"
  except Exception as e:
    logging.critical("Uncaught error: {}!".format(e))
    logging.critical(traceback.format_exc())

def speed_test():
  logging.info("beginning speed tests")
  cmd_list = ["iperf3", "-c", IPERF_SERV]
  output, error = cmd_retry(cmd_list)
  download = 0
  upload = 0
  if error:
    logging.critical("speed test failed! Exiting...")
    sys.exit(1)
  if not error:
    lines = str(output).split("\\n")
    download = lines[-5].split()[4]
    upload = lines[-4].split()[4]

  logging.info("download: {} Mbps".format(download))
  logging.info("upload: {} Mbps".format(upload))
  return download, upload

def ping_test():
  logging.info("beginning ping tests")
  cmd_list = ["ping6", "-c", str(PING_COUNT), GOOGLE_DNS_V6]
  output, error = cmd_retry(cmd_list)
  pktloss = 100
  latency = 0
  if not error:
    lines = str(output).split()
    pktloss = lines[-9].strip("%")
    latency = lines[-2].split("/")[1]

  logging.info("Packet loss: {} %".format(pktloss))
  logging.info("Avg latency: {} ms".format(latency))
  return pktloss, latency

def write(csv_file, data):
  # save the data to file for local network plotting
  # data should be a list
  logging.info("writing results to file: {}".format(csv_file))
  out_file = open(csv_file, "a")
  writer = csv.writer(out_file)
  write_data = [time.strftime(TIME_FMT_WRITE)]
  write_data.extend(data)
  writer.writerow(write_data)
  out_file.close()

def draw(csv_file, img_file):
  logging.info("reading results file {} and drawing".format(csv_file))
  y, x, xticks, y_max = [], [], [], []
  csv_reader = csv.reader(open(csv_file))

  isLine2 = False
  for line in csv_reader:
    line_time = DT.datetime.strptime(line[0], TIME_FMT_WRITE)
    x.append(line_time)
    xticks.append("")
    y.append(float(line[1]))
    if len(line) > 2:
      isLine2 = True
      y_max.append(float(line[2]))

  fig = plt.figure(figsize=(10,5), dpi=150)
  ax = fig.add_subplot(111)
  fig.subplots_adjust(bottom=0.35)

  date_as_numbers = [date2num(date) for date in x]

  label1 = "Down"
  label2 = "Up"
  plt.title("Network")
  if img_file == SPEED_IMG_FILE:
    label1 = "Download"
    label2 = "Upload"
    plt.title("Speed (Mbps)")
  elif img_file == LAT_IMG_FILE:
    label1 = "Latency"
    plt.title("Latency (ms)")
  elif img_file == PKTLOSS_IMG_FILE:
    label1 = "Packet loss"
    plt.title("Packet loss (pct)")
    
  line1 = ax.plot(date_as_numbers, y, label=label1)
  if isLine2:
    line2 = ax.plot(date_as_numbers, y_max, label=label2)

  legend = ax.legend(loc="lower right", shadow=True)
  frame = legend.get_frame()
  frame.set_facecolor("0.90")

  plt.xticks(x, xticks)
  plt.xticks(rotation="vertical")

  fig.savefig(img_file, bbox_inches="tight")

def init_logging():
  logging.basicConfig(format="%(asctime)s[%(levelname)s]: %(message)s",
                      datefmt=TIME_FMT_WRITE,
                      filename=LOG_FILE,
                      level=logging.INFO,
  )

def main():
  init_logging()
  logging.info("script started")

  down, up = speed_test()
  write(SPEED_CSV_FILE, [down, up])
  draw(SPEED_CSV_FILE, SPEED_IMG_FILE)

  pktloss, latency = ping_test()
  write(PKTLOSS_CSV_FILE, [pktloss])
  draw(PKTLOSS_CSV_FILE, PKTLOSS_IMG_FILE)

  write(LAT_CSV_FILE, [latency])
  draw(LAT_CSV_FILE, LAT_IMG_FILE)

  logging.info("script finished")

if __name__ == "__main__":
  main()
