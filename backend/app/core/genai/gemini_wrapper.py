import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = """
You are helping someone create a dashboard.

Your job is to look at a sample of their data and then ask a series of questions
to help you undestand what the person wants to accomplish with their dashboard.
Once you have enough information you will generate the complete dashboard code using streamlit. 
The code should be general and be able to run with no user intervention.
Use environment variables as needed and define them at the very top of the code. For the data, always use the env var CSV_PATH=os.getenv("CSV_PATH").
If you respond with code, you cannot include anything else. No context or explanations. Only code enclosed in ```python<code>```

Here is some examples dashboard written in streamlit:

```python
from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Use Pygwalker In Streamlit",
    layout="wide"
)

# Add Title
st.title("Use Pygwalker In Streamlit")

# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    df = pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec="./gw_config.json")


renderer = get_pyg_renderer()

st.subheader("Display Explore UI")

tab1, tab2, tab3, tab4 = st.tabs(
    ["graphic walker", "data profiling", "graphic renderer", "pure chart"]
)

with tab1:
    renderer.explorer()

with tab2:
    renderer.explorer(default_tab="data")

with tab3:
    renderer.viewer()

with tab4:
    st.markdown("### registered per weekday")
    renderer.chart(0)
    st.markdown("### registered per day")
    renderer.chart(1)
```

```python
import json
import streamlit as st
import hiplot as hip

x1, x2, x3 = st.slider('x1'), st.slider('x2'), st.slider('x3')

# Create your experiment as usual
data = [{'uid': 'a', 'dropout': 0.1, 'lr': 0.001, 'loss': 10.0, 'optimizer': 'SGD', 'x': x1},
        {'uid': 'b', 'dropout': 0.15, 'lr': 0.01, 'loss': 3.5, 'optimizer': 'Adam', 'x': x2},
        {'uid': 'c', 'dropout': 0.3, 'lr': 0.1, 'loss': 4.5, 'optimizer': 'Adam', 'x': x3}]
xp = hip.Experiment.from_iterable(data)

# Instead of calling directly `.display()`
# just convert it to a streamlit component with `.to_streamlit()` before
ret_val = xp.to_streamlit(ret="selected_uids", key="hip").display()

st.markdown("hiplot returned " + json.dumps(ret_val))
```

```python
import streamlit as st
import hiplot as hip
import hiplot.fetchers_demo

x1, x2, x3 = st.slider('x1'), st.slider('x2'), st.slider('x3')


@st.cache
def get_experiment():
    # We create a large experiment with 1000 rows
    big_exp = hiplot.fetchers_demo.demo(1000)
    # EXPERIMENTAL: Reduces bandwidth at first load
    big_exp._compress = True
    # ... convert it to streamlit and cache that (`@st.cache` decorator)
    return big_exp.to_streamlit(key="hiplot")


xp = get_experiment()  # This will be cached the second time
xp.display()
```

```python
import streamlit as st
import pandas as pd
import numpy as np

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)
```
"""


def start_gemini_session(lite: bool = False) -> genai.ChatSession:
  if lite:
      model = genai.GenerativeModel(
          model_name="gemini-1.0-pro",
          generation_config=generation_config,
          # system_instruction=system_instruction,
          safety_settings=safety_settings
      )
  else:
      model = genai.GenerativeModel(
          model_name="gemini-1.5-pro-latest",
          generation_config=generation_config,
          system_instruction=system_instruction,
          safety_settings=safety_settings
      )

  model._system_instruction
  convo = model.start_chat(history=[])
  return convo

# not in use for now, may use if we need custom logic for the gemini session
class GeminiSession:
    def __init__(self) -> None:
        self.__history = []
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
    
    def __add_message(self, message: str, role: str) -> None:
        self.__history.append({
            "role": role,
            "parts": [message]
        })

    def last_message(self) -> dict[str, str]:
        return self.__history[-1]

    async def generate_response(self, message: str) -> str:
        self.__add_message(message, "user")
        response = await self.model.generate_content_async(self.__history)
        resp_text = response.text
        self.__add_message(resp_text, "model")
        return resp_text