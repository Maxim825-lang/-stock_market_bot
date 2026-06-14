"""
Resolves user input (Russian company names, English names, tickers)
to a standard Yahoo Finance ticker symbol.
"""

COMPANY_MAP: dict[str, dict] = {
    # Russian companies — full names and transliterations
    "сбербанк": {"ticker": "SBER.ME", "name": "Сбербанк"},
    "сбер": {"ticker": "SBER.ME", "name": "Сбербанк"},
    "sber": {"ticker": "SBER.ME", "name": "Сбербанк"},
    "газпром": {"ticker": "GAZP.ME", "name": "Газпром"},
    "gazprom": {"ticker": "GAZP.ME", "name": "Газпром"},
    "лукойл": {"ticker": "LKOH.ME", "name": "Лукойл"},
    "lukoil": {"ticker": "LKOH.ME", "name": "Лукойл"},
    "яндекс": {"ticker": "YDEX.ME", "name": "Яндекс"},
    "yandex": {"ticker": "YDEX.ME", "name": "Яндекс"},
    "роснефть": {"ticker": "ROSN.ME", "name": "Роснефть"},
    "rosneft": {"ticker": "ROSN.ME", "name": "Роснефть"},
    "норникель": {"ticker": "GMKN.ME", "name": "Норникель"},
    "norilsk": {"ticker": "GMKN.ME", "name": "Норникель"},
    "новатэк": {"ticker": "NVTK.ME", "name": "Новатэк"},
    "novatek": {"ticker": "NVTK.ME", "name": "Новатэк"},
    "татнефть": {"ticker": "TATN.ME", "name": "Татнефть"},
    "tatneft": {"ticker": "TATN.ME", "name": "Татнефть"},
    "втб": {"ticker": "VTBR.ME", "name": "ВТБ"},
    "vtb": {"ticker": "VTBR.ME", "name": "ВТБ"},
    "магнит": {"ticker": "MGNT.ME", "name": "Магнит"},
    "magnit": {"ticker": "MGNT.ME", "name": "Магнит"},
    "мтс": {"ticker": "MTSS.ME", "name": "МТС"},
    "mts": {"ticker": "MTSS.ME", "name": "МТС"},
    "северсталь": {"ticker": "CHMF.ME", "name": "Северсталь"},
    "severstal": {"ticker": "CHMF.ME", "name": "Северсталь"},
    "алроса": {"ticker": "ALRS.ME", "name": "Алроса"},
    "alrosa": {"ticker": "ALRS.ME", "name": "Алроса"},
    "интер рао": {"ticker": "IRAO.ME", "name": "Интер РАО"},
    "интеррао": {"ticker": "IRAO.ME", "name": "Интер РАО"},
    "пик": {"ticker": "PIKK.ME", "name": "ПИК"},
    "афк система": {"ticker": "AFKS.ME", "name": "АФК Система"},
    "система": {"ticker": "AFKS.ME", "name": "АФК Система"},
    # Russian companies — direct MOEX short tickers (so SBER/GAZP/etc. work without .ME)
    "gazp": {"ticker": "GAZP.ME", "name": "Газпром"},
    "lkoh": {"ticker": "LKOH.ME", "name": "Лукойл"},
    "ydex": {"ticker": "YDEX.ME", "name": "Яндекс"},
    "rosn": {"ticker": "ROSN.ME", "name": "Роснефть"},
    "vtbr": {"ticker": "VTBR.ME", "name": "ВТБ"},
    "gmkn": {"ticker": "GMKN.ME", "name": "Норникель"},
    "nvtk": {"ticker": "NVTK.ME", "name": "Новатэк"},
    "tatn": {"ticker": "TATN.ME", "name": "Татнефть"},
    "mgnt": {"ticker": "MGNT.ME", "name": "Магнит"},
    "mtss": {"ticker": "MTSS.ME", "name": "МТС"},
    "chmf": {"ticker": "CHMF.ME", "name": "Северсталь"},
    "alrs": {"ticker": "ALRS.ME", "name": "Алроса"},
    "irao": {"ticker": "IRAO.ME", "name": "Интер РАО"},
    "pikk": {"ticker": "PIKK.ME", "name": "ПИК"},
    "afks": {"ticker": "AFKS.ME", "name": "АФК Система"},
    # US companies
    "apple": {"ticker": "AAPL", "name": "Apple"},
    "tesla": {"ticker": "TSLA", "name": "Tesla"},
    "nvidia": {"ticker": "NVDA", "name": "Nvidia"},
    "microsoft": {"ticker": "MSFT", "name": "Microsoft"},
    "google": {"ticker": "GOOGL", "name": "Google (Alphabet)"},
    "alphabet": {"ticker": "GOOGL", "name": "Google (Alphabet)"},
    "amazon": {"ticker": "AMZN", "name": "Amazon"},
    "meta": {"ticker": "META", "name": "Meta"},
    "facebook": {"ticker": "META", "name": "Meta"},
    "netflix": {"ticker": "NFLX", "name": "Netflix"},
    "intel": {"ticker": "INTC", "name": "Intel"},
    "amd": {"ticker": "AMD", "name": "AMD"},
    "berkshire": {"ticker": "BRK-B", "name": "Berkshire Hathaway"},
    "jpmorgan": {"ticker": "JPM", "name": "JPMorgan Chase"},
    "jp morgan": {"ticker": "JPM", "name": "JPMorgan Chase"},
    "coca cola": {"ticker": "KO", "name": "Coca-Cola"},
    "кока кола": {"ticker": "KO", "name": "Coca-Cola"},
    "disney": {"ticker": "DIS", "name": "Walt Disney"},
    "дисней": {"ticker": "DIS", "name": "Walt Disney"},
    "boeing": {"ticker": "BA", "name": "Boeing"},
    "боинг": {"ticker": "BA", "name": "Boeing"},
    "exxon": {"ticker": "XOM", "name": "ExxonMobil"},
    "visa": {"ticker": "V", "name": "Visa"},
    "mastercard": {"ticker": "MA", "name": "Mastercard"},
    "pfizer": {"ticker": "PFE", "name": "Pfizer"},
    "пфайзер": {"ticker": "PFE", "name": "Pfizer"},
    "johnson": {"ticker": "JNJ", "name": "Johnson & Johnson"},
    "walmart": {"ticker": "WMT", "name": "Walmart"},
    "paypal": {"ticker": "PYPL", "name": "PayPal"},
    "uber": {"ticker": "UBER", "name": "Uber"},
    "airbnb": {"ticker": "ABNB", "name": "Airbnb"},
    "salesforce": {"ticker": "CRM", "name": "Salesforce"},
    "oracle": {"ticker": "ORCL", "name": "Oracle"},
    "ibm": {"ticker": "IBM", "name": "IBM"},
    "twitter": {"ticker": "X", "name": "X (Twitter)"},
    "x": {"ticker": "X", "name": "X (Twitter)"},
    "snapchat": {"ticker": "SNAP", "name": "Snap Inc."},
    "snap": {"ticker": "SNAP", "name": "Snap Inc."},
    "spotify": {"ticker": "SPOT", "name": "Spotify"},
    "shopify": {"ticker": "SHOP", "name": "Shopify"},
    "palantir": {"ticker": "PLTR", "name": "Palantir"},
    "coinbase": {"ticker": "COIN", "name": "Coinbase"},
    "robinhood": {"ticker": "HOOD", "name": "Robinhood"},
    "rivian": {"ticker": "RIVN", "name": "Rivian"},
    "lucid": {"ticker": "LCID", "name": "Lucid Motors"},
}

# Companies known to be private (not publicly traded)
PRIVATE_COMPANIES: dict[str, str] = {
    "spacex": "SpaceX",
    "спейсэкс": "SpaceX",
    "openai": "OpenAI",
    "openai inc": "OpenAI",
    "anthropic": "Anthropic",
    "stripe": "Stripe",
    "bytedance": "ByteDance",
    "huawei": "Huawei",
    "ikea": "IKEA",
    "lego": "LEGO",
}

# Indices / ETFs
INDEX_MAP: dict[str, dict] = {
    "sp500": {"ticker": "^GSPC", "name": "S&P 500"},
    "s&p 500": {"ticker": "^GSPC", "name": "S&P 500"},
    "dow jones": {"ticker": "^DJI", "name": "Dow Jones"},
    "nasdaq": {"ticker": "^IXIC", "name": "NASDAQ"},
    "ммвб": {"ticker": "IMOEX.ME", "name": "Индекс МосБиржи"},
    "мосбиржа": {"ticker": "IMOEX.ME", "name": "Индекс МосБиржи"},
    "imoex": {"ticker": "IMOEX.ME", "name": "Индекс МосБиржи"},
    "btc": {"ticker": "BTC-USD", "name": "Bitcoin"},
    "bitcoin": {"ticker": "BTC-USD", "name": "Bitcoin"},
    "биткоин": {"ticker": "BTC-USD", "name": "Bitcoin"},
    "eth": {"ticker": "ETH-USD", "name": "Ethereum"},
    "ethereum": {"ticker": "ETH-USD", "name": "Ethereum"},
}


class TickerResolutionResult:
    """Result of ticker resolution."""

    def __init__(
        self,
        ticker: str | None,
        company_name: str,
        is_private: bool = False,
        private_message: str = "",
        original_input: str = "",
        is_known: bool = True,
    ):
        self.ticker = ticker
        self.company_name = company_name
        self.is_private = is_private
        self.private_message = private_message
        self.original_input = original_input
        # False when input was passed through as-is (not found in any map)
        self.is_known = is_known

    @property
    def found(self) -> bool:
        return self.ticker is not None or self.is_private


def resolve_ticker(user_input: str) -> TickerResolutionResult:
    """
    Resolve user input to a ticker symbol.

    Handles:
    - Russian company names (сбербанк → SBER.ME)
    - English company names (apple → AAPL)
    - Direct ticker symbols (AAPL, SBER.ME)
    - Private companies (spacex → explanation)
    - Indices and crypto
    """
    raw = user_input.strip()
    normalized = raw.lower().replace("'", "").replace("-", " ").strip()

    # Check private companies first (exact match or longer substring, min 4 chars to avoid e.g. "x" matching "spacex")
    for key, name in PRIVATE_COMPANIES.items():
        if normalized == key or (len(normalized) >= 4 and len(key) >= 4 and (key in normalized or normalized in key)):
            return TickerResolutionResult(
                ticker=None,
                company_name=name,
                is_private=True,
                private_message=_private_company_message(name),
                original_input=raw,
            )

    # Check known company map
    if normalized in COMPANY_MAP:
        entry = COMPANY_MAP[normalized]
        return TickerResolutionResult(
            ticker=entry["ticker"],
            company_name=entry["name"],
            original_input=raw,
        )

    # Check index / crypto map
    if normalized in INDEX_MAP:
        entry = INDEX_MAP[normalized]
        return TickerResolutionResult(
            ticker=entry["ticker"],
            company_name=entry["name"],
            original_input=raw,
        )

    # Partial match in company map (e.g. "сбер" inside "сбербанк")
    # Require minimum length to avoid single-char false positives
    for key, entry in {**COMPANY_MAP, **INDEX_MAP}.items():
        if len(normalized) >= 3 and len(key) >= 3 and (normalized in key or key in normalized):
            return TickerResolutionResult(
                ticker=entry["ticker"],
                company_name=entry["name"],
                original_input=raw,
            )

    # Assume it's a direct ticker symbol — pass through as uppercase
    ticker_upper = raw.upper()
    return TickerResolutionResult(
        ticker=ticker_upper,
        company_name=ticker_upper,
        original_input=raw,
        is_known=False,  # not found in any map; may still be a valid exchange ticker
    )


def _private_company_message(name: str) -> str:
    related = {
        "SpaceX": (
            "SpaceX — частная компания и не имеет публичного биржевого тикера. "
            "Вы можете проанализировать связанные публичные компании:\n"
            "• <b>BA</b> (Boeing) — конкурент в аэрокосмической отрасли\n"
            "• <b>LMT</b> (Lockheed Martin) — аэрокосмос и оборона\n"
            "• <b>TSLA</b> (Tesla) — компания Илона Маска\n\n"
            "Попробуйте: /analyze TSLA или /analyze LMT"
        ),
        "OpenAI": (
            "OpenAI — частная компания, акции на бирже не торгуются. "
            "Можно рассмотреть публичных участников рынка ИИ:\n"
            "• <b>NVDA</b> (Nvidia) — чипы для ИИ\n"
            "• <b>MSFT</b> (Microsoft) — крупный инвестор OpenAI\n"
            "• <b>GOOGL</b> (Alphabet/Google) — конкурент в сфере ИИ"
        ),
        "Anthropic": (
            "Anthropic — частная компания. "
            "Для ИИ-сектора смотрите: NVDA, MSFT, GOOGL"
        ),
    }
    return related.get(
        name,
        f"{name} — частная компания и не торгуется на публичных биржах. "
        "Введите тикер публичной компании для анализа.",
    )
