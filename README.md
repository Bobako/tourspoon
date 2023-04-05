# TourSpoon

Some description

[icons to use](https://css.gg/app)

### Setup

#### On dev machine

1. Python3.10 with pip and venv required
2. ```python -m venv venv```
3. ```./venv/Scripts/activate```
4. ```pip install -r requirments.txt```
5. ```python main.py```

#### On linux prod machine

1. Nginx, python with pip and venv, supervisor required
2. Configure nginx port proxy (:80 to :app_port (see config.ini))
3. Configure environment (as shown on dev machine block)
4. Configure supervisor to autostart tourspoon
5. ?
6. Profit
