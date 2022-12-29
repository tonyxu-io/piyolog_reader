import enum
import os
import datetime
import numpy as np
import pandas as pd

def make_feces_record(index, value_string):
  volume = "ふつう"
  consistency = "ふつう"
  if value_string is None:
    pass
  elif "ちょこっと" in value_string:
    volume = "ちょこっと"
  elif "少なめ" in value_string:
    volume = "少なめ"
  elif "多め" in value_string:
    volume = "多め"
  elif "下痢" in value_string:
    consistency = "下痢"
  elif "やわらかめ" in value_string:
    consistency = "やわらかめ" 
  elif "かため" in value_string:
    consistency = "かため" 
  record = {
    "index": index, "volume": volume, "consistency": consistency,
  }
  return record

def make_go_to_bed_record(index, value_string):
  error = False
  if value_string is not None:
    error = True
  record = {"index": index, "error": error}
  return record

def make_get_up_record(index, timestamp, value_string):
  hours = 0
  minutes = 0
  if "!" in value_string:
      record = {"index": index, "sleeping_time": None, "wake_up_time": timestamp, "bedtime": None, "error": True}
  else:
    hours_end = value_string.find("時間")
    hours = int(value_string[1:hours_end])
    minutes_end = value_string.find("分")
    minutes = int(value_string[hours_end+2:minutes_end])
    sleeping_time = datetime.timedelta(hours=hours, minutes=minutes)
    wake_up_time = timestamp
    bedtime = timestamp - wake_up_time
    record = {"index": index, "sleeping_time": sleeping_time, "wake_up_time": wake_up_time, "bedtime": bedtime, "error": False}  
  return record

def make_expressed_breast_milk_record(index, value_string):
  volume_end = value_string.find("ml")
  volume = int(value_string[:volume_end])
  record = {"index": index, "volume": volume}
  return record

def make_milk_record(index, value_string):
  if value_string is None:
    volume = None
  else:
    volume_end = value_string.find("ml")
    volume = int(value_string[:volume_end])
  record = {"index": index, "volume": volume}
  return record

def make_breast_milk_record(index, value_string):
  volume = None
  left_minutes = None
  right_minutes = None
  order = None
  if value_string is None:
    volume = None
  elif "ml" in value_string:
    volume_start = value_string.find("(") + 1
    volume_end = value_string.find("ml")
    volume = int(value_string[volume_start:volume_end])
  elif "母乳" == value_string:
    volume = None
  elif ("左" in value_string) and ("右" in value_string):
    left_minutes_start = value_string.find("左") + 1
    left_value_string = value_string[left_minutes_start:]
    left_minutes = int(left_value_string[:left_value_string.find("分")])
    right_minutes_start = value_string.find("右") + 1
    right_value_string = value_string[right_minutes_start:]
    right_minutes = int(right_value_string[:right_value_string.find("分")])
    if "/" in value_string:
      order = None
    elif "▶" in value_string:
      order = "left_to_right"
    elif "◀" in value_string:
      order = "right_to_left"
    else:
      raise ValueError("unknown value string", value_string)
  elif "左" in value_string:
    left_minutes_start = value_string.find("左") + 1
    left_value_string = value_string[left_minutes_start:]
    left_minutes = int(left_value_string[:left_value_string.find("分")])
  elif "右" in value_string:
    right_minutes_start = value_string.find("右") + 1
    right_value_string = value_string[right_minutes_start:]
    right_minutes = int(right_value_string[:right_value_string.find("分")])
  else:
    raise ValueError("unknown value string", value_string)
  record = {
    "index": index, 
    "volume": volume, 
    "left_minutes": left_minutes, 
    "right_minutes": right_minutes,
    "order": order,
  }
  return record

def make_height_record(index, value_string):
  height_end = value_string.find("cm")
  height = float(value_string[:height_end])
  record = {"index": index, "height": height}
  return record

def make_weight_record(index, value_string):
  weight_end = value_string.find("kg")
  weight = float(value_string[:weight_end])
  record = {"index": index, "weight": weight}
  return record

def make_temperature_record(index, value_string):
  temperature = float(value_string[:value_string.find("°C")])
  record = {
    "index": index, 
    "temperature": temperature,
  }
  return record

class State(enum.Enum):
    START = enum.auto()
    DATE = enum.auto()
    NAME = enum.auto()
    BLANK_AFTER_NAME = enum.auto()
    EVENT = enum.auto()
    STATS = enum.auto()
    COMMNET = enum.auto()

def read_text(text_path, index_offset=0):
  #print(text_path)
  date = None
  baby_data = {}
  date_df_list = []
  event_df_list = []
  go_to_bed_df_list = []
  get_up_df_list = []
  height_df_list = []
  weight_df_list = []
  temperature_df_list = []
  expressed_breast_milk_df_list = []
  milk_df_list = []
  breast_milk_df_list = []
  feces_df_list = []

  state = State.START
  name = None
  age = None
  commnet = None
  local_timezone = datetime.timezone(datetime.timedelta(hours=9), "Asia/Tokyo")
  index = index_offset
  date_data_record = None
  with open(text_path) as f:
    for i, line in enumerate(f):
      line = line.strip()
      #print(i, line)
      #if i >= 100:
      #  break 
      if len(line) == 0 and state == State.BLANK_AFTER_NAME:
        state = State.EVENT
        continue
      elif len(line) == 0 and state == State.EVENT:
        #print("to STATS")
        state = State.STATS
        continue
      elif len(line) == 0 and state == State.STATS:
        #print("to START")
        state = State.COMMNET
        continue
      elif len(line) == 0 and state == State.STATS:
        #print("to START")
        state = State.START
        continue
      elif line == "----------":
        if date_data_record is not None:
          date_data_record["comment"] = commnet
          date_df_list.append(date_data_record)
        date_data_record = None
        commnet = None
        state = State.DATE
        continue
      elif State.DATE == state:
        date = datetime.datetime.strptime(line[:-3], '%Y/%m/%d')
        #print("date", date)
        state = State.NAME
        continue
      elif state == State.NAME:
        s = line.find(" ")
        name = line[:s]
        baby_data["name"] = name
        #print("name", name)
        age_str_start = line.find("(")
        age_year_end = line.find("歳")
        age_month_end = line.find("か月")
        age_day_end = line.find("日")
        date_data_record = {
            "date": date,
            "age_year": int(line[age_str_start+1:age_year_end]),
            "age_month": int(line[age_year_end+1:age_month_end]),
            "age_day": int(line[age_month_end+2:age_day_end])
        }
        state = State.BLANK_AFTER_NAME
        continue
      elif state == State.EVENT:
        #print("event", line)
        event_time = datetime.datetime.strptime(line[:5], '%H:%M')
        event_datetime = datetime.datetime(
          year=date.year,
          month=date.month,
          day=date.day,
          hour=event_time.hour,
          minute=event_time.minute,
          tzinfo=local_timezone
        )
        event_value_string = line[8:]
        event_string = event_value_string
        envet_name_end = event_value_string.find(" ")
        value_string = None
        if envet_name_end > 0:
          event_string = event_value_string[:envet_name_end]
          value_string = event_value_string[envet_name_end + 1:]
        event_record = {
          "index": index,
          "timestamp": event_datetime,
          "event": event_string,
        }
        event_df_list.append(event_record)
        if event_string == "寝る":
          record = make_go_to_bed_record(index=index, value_string=value_string)
          go_to_bed_df_list.append(record)
        elif event_string == "起きる":
          record = make_get_up_record(index, event_datetime, value_string)
          get_up_df_list.append(record)
        elif event_string == "身長":
          record = make_height_record(index, value_string=value_string)
          height_df_list.append(record)
        elif event_string == "体重":
          record = make_weight_record(index, value_string=value_string)
          weight_df_list.append(record)
        elif event_string == "体温":
          record = make_temperature_record(index, value_string=value_string)
          temperature_df_list.append(record)
        elif event_string == "搾母乳":
          record = make_expressed_breast_milk_record(
            index=index,
            value_string=value_string,
          )
          expressed_breast_milk_df_list.append(record)
        elif event_string == "ミルク":
          record = make_milk_record(
            index=index,
            value_string=value_string,
          )
          milk_df_list.append(record)
        elif event_string == "母乳":
          record = make_breast_milk_record(
            index=index,
            value_string=value_string,
          )
          breast_milk_df_list.append(record)
        elif event_string == "うんち":
          record = make_feces_record(
            index=index,
            value_string=value_string,
          )
          feces_df_list.append(record)
        elif value_string is not None:
          raise RuntimeError("unknown event has value string", event_string, value_string)
        else:
          record = None
        index += 1
      elif state == State.STATS:
        pass
      elif state == State.START and "ぴよログ" in line:
        pass
      elif state == State.COMMNET:
        if commnet is None:
          commnet = ""
        commnet += line + "\n"
      else:
        raise RuntimeError("unknown", line)
        
    date_df = pd.DataFrame(date_df_list)
    event_df = pd.DataFrame(event_df_list)
    if len(event_df) == 0:
      event_df = pd.DataFrame(
        {
          "index": [],
          "timestamp": [],
          "event": [],
        }
      )
    event_df = event_df.set_index("index")

    go_to_bed_df = pd.DataFrame(go_to_bed_df_list)
    if len(go_to_bed_df) == 0:
      go_to_bed_df = pd.DataFrame(
        {"index": [], "error": []}
      )
    go_to_bed_df = go_to_bed_df.set_index("index")

    get_up_df = pd.DataFrame(get_up_df_list)
    if len(get_up_df) == 0:
      get_up_df = pd.DataFrame(
         {"index": [], "sleeping_time": [], "wake_up_time": [], "bedtime": [], "error": []}  
      )
    get_up_df = get_up_df.set_index("index")

    height_df = pd.DataFrame(height_df_list)
    if len(height_df) == 0:
      height_df = pd.DataFrame(
         {"index": [], "height": []}  
      )
    height_df = height_df.set_index("index")

    weight_df = pd.DataFrame(weight_df_list)
    if len(weight_df) == 0:
      weight_df = pd.DataFrame(
         {"index": [], "weight": []}  
      )
    weight_df = weight_df.set_index("index")

    temperature_df = pd.DataFrame(temperature_df_list)
    if len(temperature_df) == 0:
      temperature_df = pd.DataFrame(
        {
           "index": [], 
           "temperature": [],
        }
      )
    temperature_df = temperature_df.set_index("index")
    
    expressed_breast_milk_df = pd.DataFrame(expressed_breast_milk_df_list)
    if len(expressed_breast_milk_df) == 0:
      expressed_breast_milk_df = pd.DataFrame(
         {"index": [], "volume": []}
      )
    expressed_breast_milk_df = expressed_breast_milk_df.set_index("index")

    milk_df = pd.DataFrame(milk_df_list)
    if len(milk_df) == 0:
      milk_df = pd.DataFrame(
         {"index": [], "volume": []}
      )
    milk_df = milk_df.set_index("index")

    breast_milk_df = pd.DataFrame(breast_milk_df_list)
    if len(breast_milk_df) == 0:
      breast_milk_df = pd.DataFrame(
        {
          "index": [],
          "volume": [], 
          "left_minutes": [], 
          "right_minutes": [],
          "order": [],
        }
      )
    breast_milk_df = breast_milk_df.set_index("index")

    feces_df = pd.DataFrame(feces_df_list)
    if len(feces_df) == 0:
      feces_df = pd.DataFrame(
        {
          "index": [], "volume": [], "consistency": [],
        }
      )
    feces_df = feces_df.set_index("index")
    dfs = {
      "date": date_df,
      "event": event_df,
      "go_to_bed": go_to_bed_df,
      "get_up": get_up_df,
      "height": height_df,
      "weight": weight_df,
      "temperature": temperature_df,
      "expressed_breast_milk": expressed_breast_milk_df,
      "milk": milk_df,
      "breast_milk": breast_milk_df,
      "feces": feces_df,
    }
    return dfs, index,

def read_texts(text_pathes):
  index_offset = 0
  ret = None
  for p in text_pathes:
    dfs, index_offset = read_text(text_path=p, index_offset=index_offset)
    if ret is None:
      ret = dfs
    else:
      for key, df in dfs.items():
        assert set(ret[key].columns) == set(df.columns)
        ret[key] = pd.concat([ret[key], df])
  return ret