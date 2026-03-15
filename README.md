# Walmonitor

## Overview

Walmonitor is a dashboard for visualizing the performance of Walmart stores across different branches and time periods. It provides insights into sales trends, product line rankings, and other key performance indicators to help stakeholders make informed decisions.

## Project maintainers

* [Jacob Cann](https://github.com/Jacob-F-Cann)
* [Mailys Guedon](https://github.com/mailysg8)
* [Yuheng Ouyang](https://github.com/yhouyang02)
* [Li Pu](https://github.com/Coachyyds)

## Users

The primary users of this dashboard are Walmart store managers and regional directors who need to monitor store performance and make data-driven decisions. Prospective users also include analysts and executives who require insights into sales trends and product performance across the company. You can check out what the dashboard provides from the web app (adjust your browser zoom level for the best viewing experience):

* Stable: <https://yhouyang02-walmonitor.share.connect.posit.cloud/>
* Preview: <https://019c9e5b-677b-b15d-18c3-2f360a7b781a.share.connect.posit.cloud/>

For a demo on how to use the dashboard, please refer to the animation:

![Demo animation](./img/demo.gif)

You can also apply your own dataset to the dashboard by following the instructions in the next section. Simply replace the `data/raw/walmart_sales_data.csv` file with your dataset (make sure to keep the same format and column names) and run the app locally.

The dataset in the shown in the repository and shiny app was obtained from the [Walmart-Sales-Data-Analysis](https://github.com/MohammedShehbazDamkar/Walmart-Sales-Data-Analysis--SQL-Project/blob/main/Walmart%20Sales%20Data.csv.csv) public repository by  [Mohammed Shehbaz Damkar](https://github.com/MohammedShehbazDamkar).

## Contributors

You can run this app locally following the instructions below.

1. Clone this repository:

    ```bash
    git clone https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor.git
    ```

2. Navigate to the project directory locally:

    ```bash
    cd DSCI-532_2026_2_walmonitor
    ```

3. Install the required dependencies (we recommend using `conda`):

    ```bash
    conda env create -f environment.yml
    conda activate walmonitor
    ```

    Alternatively, you can install the dependencies using `pip`:

    ```bash
    pip install -r requirements.txt  # not required if using conda
    ```

4. Run the app in reload mode:

    ```bash
    shiny run --reload src/app.py
    ```

5. Check the terminal for the local URL (e.g., `http://127.0.0.1:8000`) and open it in your web browser to view the dashboard.

To contribute to this project, please refer to the [contribution guidelines](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md).

## Tests

To run the unit tests, follow these instructions:

1. Follow the first 3 steps in the [Contributors](#contributors) section above to clone the repository.

2. In the root of the directory, run the following command:

    ```bash
    pytest
    ```

## LLM usage disclosure

Large language models (LLMs) were used to assist the development of this project. We did our best to ensure that the use of LLMs was ethical and transparent. Below is a table summarizing the LLMs we used, their purposes, and the last time we accessed them.

| Model | Usage | Last Accessed |
| --- | --- | --- |
| [GitHub Copilot](https://github.com/features/copilot) | Pull request review, code fix, style consistency | March 2026 |
| [GPT-5.2](https://openai.com/index/introducing-gpt-5-2/) | Dashboard sketch generation | February 2026 |
| [GPT-4.1 mini](https://openai.com/index/gpt-4-1/) | Chatbot integration | March 2026 |

## Copyright

Copyright © 2026 Jacob Cann, Mailys Guedon, Yuheng Ouyang, Li Pu.  
Free software distributed under the MIT License.
