from buy_gate import AccountState, ProposedBuy, check_buy


def baseline_account() -> AccountState:
    return AccountState(
        equity=100_000.0,
        cash=80_000.0,
        open_position_count=3,
        weekly_trade_count=1,
        day_trade_count=0,
    )


def baseline_trade() -> ProposedBuy:
    return ProposedBuy(
        symbol="AAPL",
        shares=100,
        ask_price=150.0,  # $15,000 cost = 15% of equity, fits all rules
        catalyst_documented=True,
        is_stock=True,
    )


def test_baseline_trade_is_allowed():
    result = check_buy(baseline_account(), baseline_trade())
    assert result.allowed, result.failures


def test_options_are_rejected():
    trade = ProposedBuy(symbol="AAPL250620C150", shares=1, ask_price=5.0,
                       catalyst_documented=True, is_stock=False)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("not a stock" in f for f in result.failures)


def test_sixth_position_is_rejected():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=6,
                          weekly_trade_count=0, day_trade_count=0)
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("max positions" in f for f in result.failures)


def test_fourth_weekly_trade_is_rejected():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=3, day_trade_count=0)
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("weekly trade cap" in f for f in result.failures)


def test_position_over_20pct_is_rejected():
    # 200 shares × $150 = $30k = 30% of $100k equity
    trade = ProposedBuy(symbol="AAPL", shares=200, ask_price=150.0,
                       catalyst_documented=True, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("20% of equity" in f for f in result.failures)


def test_position_over_cash_is_rejected():
    account = AccountState(equity=100_000, cash=5_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=0)
    # $15k cost > $5k cash. Note this also fails the 20% rule if equity was lower —
    # here equity=$100k so 20% = $20k, so this isolates the cash check.
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("available cash" in f for f in result.failures)


def test_pdt_limit_is_rejected():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=3)
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("PDT" in f for f in result.failures)


def test_missing_catalyst_is_rejected():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=False, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("catalyst" in f for f in result.failures)


def test_multiple_failures_all_reported():
    account = AccountState(equity=100_000, cash=5_000, open_position_count=6,
                          weekly_trade_count=3, day_trade_count=3)
    trade = ProposedBuy(symbol="OPTION", shares=200, ask_price=150.0,
                       catalyst_documented=False, is_stock=False)
    result = check_buy(account, trade)
    assert not result.allowed
    assert len(result.failures) >= 5  # all distinct rules tripped


def test_exactly_at_20pct_is_allowed():
    # 200 × $100 = $20,000 = exactly 20% of $100k equity
    trade = ProposedBuy(symbol="AAPL", shares=200, ask_price=100.0,
                       catalyst_documented=True, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_sixth_position_at_boundary():
    # 5 open + this 1 = 6, which is allowed (the rule is "<= 6")
    account = AccountState(equity=100_000, cash=80_000, open_position_count=5,
                          weekly_trade_count=0, day_trade_count=0)
    result = check_buy(account, baseline_trade())
    assert result.allowed, result.failures


def test_third_weekly_trade_at_boundary():
    # 2 this week + this 1 = 3, which is allowed (the rule is "<= 3")
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=2, day_trade_count=0)
    result = check_buy(account, baseline_trade())
    assert result.allowed, result.failures
