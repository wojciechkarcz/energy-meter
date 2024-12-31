# Grafana

This guide explains how to: 
- set up Grafana on Linux (Ubuntu), 
- connect it to an SQLite database, 
- and import a pre-configured dashboard.

<br>

## Installation

**Install Grafana**

Update your package list and install Grafana on Linux (Ubuntu):
```sh
sudo apt-get install -y apt-transport-https software-properties-common wget

sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# Updates the list of available packages
sudo apt-get update

# Installs the latest OSS release:
sudo apt-get install grafana
```

Start the Grafana service and enable it to start automatically after reboot:
 ```sh
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

**Connect to SQLite Database**
- Access Grafana at `http://localhost:3000` and log in using the default credentials (`admin/admin`).
- Go to **Configuration** > **Data Sources** > **Add Data Source**.
- Select **SQLite** and provide the path to your `energy_meter.db` database.

<br>

**Known issues with SQLite databases**

If you encounter issues accessing the SQLite database stored in the `/home` directory on the same machine as Grafana, refer to the [official documentation on common problems](https://github.com/fr-ser/grafana-sqlite-datasource?tab=readme-ov-file#common-problems---faq).

For example, if you receive a _"permission denied"_ error, try updating the permissions for the directories above the location of your SQLite file. This can be done using:

```
sudo chmod o+x /path/to/sqlite_dir
```

<br>

## Dashboard import

Grafana allows you to import/export entire dashboards using a single JSON file.

Steps to Import a Dashboard:
1. Click **Dashboards** in the primary menu.
2. Select **New** > **Import** from the drop-down menu.
3. Drag and drop the `dashboard.json` file or paste its content into the provided text area.
4. Click the **Load** button.
5. Set the dashboard name and save.

After importing, the dashboard may not display data immediately. You need to:
- Edit each chart individually and set the correct data source (in this case, the SQLite database).
- If you have set the SQLite database as the default data source, simply click the **Refresh** button in the top-left corner of each chart.

<br>

## Fine-tuning

You need to adapt the dashboard a little bit and set up your own limits, targets, prices, tariffs, etc. But `Power delta`, `Daily usage`, `Daily power consumption in past week` should work out of the box. 

I am currently working on a way to handle dashboard configuration more efficiently using an external `.yaml` file. This feature will be included in future updates.

