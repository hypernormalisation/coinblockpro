from sanic import Sanic
from sanic.log import logger
from sanic.response import json


ticker_data = {
    'a': 1200.1,
    'b': 400.34,
    'c': 500.31,
}


app = Sanic("exchange")


@app.route("/full_ticker")
async def get_full_ticker(request):
    """Get the full ticker, i.e. for all markets."""
    global ticker_data
    logger.info('Received a full ticker request.')
    return json({'result': ticker_data})


@app.route('/single_ticker')
async def get_single_ticker(request):
    """Get a single market ticker. The market parameter must be given."""
    logger.info('Received a single ticker request.')
    global ticker_data
    request_args = request.get_args()
    if 'market' not in request_args:
        return json(
            {'error': 'must give "market" parameter!'},
            status=400,
        )
    logger.debug(request_args)
    market = request_args['market'][0]
    if market not in ticker_data:
        return json(
            {'error': 'market code not recognised!'},
            status=400,
        )
    return json({'result': {market: ticker_data[market]}})


if __name__ == "__main__":
    logger.info('Running as main')
    app.run(host="0.0.0.0", port=8000)
