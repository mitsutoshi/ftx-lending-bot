# ftx-lending-bot

This script is for automating the compound interest operation of lending in ftx.

If there is a lendable balance in your account, the lending settings will be updated automatically.

## How to setup

1. Install

    ```sh
    pipenv install
    ```

2. Define environment variables

    |NAME|VALUE|
    |---|---|
    |FTX_API_KEY|API key of FTX exchange|
    |FTX_API_SECRET|API secret FTX exchange|

## How to run

Run main.py with `-c` or `--coin` option. `<coin>` is a symbol of lending currency such as `USD`, `BTC`.

```
python main.py -c <coin>
```

`-c` option is able to specify multiple values.

e.g. both `USD` and `BTC`

```
python main.py -c USD BTC
```

It is encouraged to run regularly.

