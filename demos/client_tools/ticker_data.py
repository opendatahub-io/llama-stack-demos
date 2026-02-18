# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
import json

import pandas as pd
import yfinance as yf

from llama_stack_client.lib.agents.client_tool import client_tool


@client_tool
def get_ticker_data(ticker_symbol: str, start: str, end: str) -> str:
    """
    Get yearly closing prices for a given ticker symbol

    :param ticker_symbol: The ticker symbol for which to get the data. eg. '^GSPC'
    :param start: Start date, eg. '2021-01-01'
    :param end: End date, eg. '2024-12-31'
    :return: JSON string of yearly closing prices
    """
    try:
        data = yf.download(ticker_symbol, start=start, end=end, multi_level_index=False, progress=False)
        if data.empty:
            return json.dumps({"error": f"No data found for {ticker_symbol}"})

        # Handle MultiIndex columns from yfinance (in case multi_level_index param is ignored)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        data["Year"] = data.index.year
        annual_close = data.groupby("Year")["Close"].last().reset_index()
        return annual_close.to_json(orient="records", date_format="iso")
    except Exception as e:
        return json.dumps({"error": str(e)})
