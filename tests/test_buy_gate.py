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


# ---------------- Phase A7: universe filter ----------------

def test_off_universe_ticker_is_rejected():
    trade = ProposedBuy(symbol="GME", shares=100, ask_price=20.0,
                       catalyst_documented=True, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("TRADING_UNIVERSE" in f for f in result.failures)


def test_universe_match_is_case_insensitive():
    trade = ProposedBuy(symbol="aapl", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_sector_etf_is_in_universe():
    trade = ProposedBuy(symbol="XLK", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


# ---------------- Phase A1: system kill switches ----------------

def test_lock_file_blocks_all_buys():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=0,
                          lock_file_present=True)
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("LOCK file" in f for f in result.failures)


def test_daily_dd_freeze_blocks_buys():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=0,
                          daily_dd_response="freeze_entries_48h")
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("daily DD" in f for f in result.failures)


def test_daily_dd_tighten_does_not_block_buys():
    # tighten_trails is a sell-side response — it doesn't freeze entries.
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=0,
                          daily_dd_response="tighten_trails")
    result = check_buy(account, baseline_trade())
    assert result.allowed, result.failures


def test_weekly_dd_freeze_blocks_buys():
    account = AccountState(equity=100_000, cash=80_000, open_position_count=2,
                          weekly_trade_count=0, day_trade_count=0,
                          weekly_dd_response="freeze_until_monday")
    result = check_buy(account, baseline_trade())
    assert not result.allowed
    assert any("weekly DD" in f for f in result.failures)


# ---------------- Phase A3: correlation cap ----------------

def test_high_correlation_is_rejected():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       max_correlation_with_existing=0.85)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("correlation" in f for f in result.failures)


def test_correlation_at_boundary_is_allowed():
    # rule is "> 0.70" rejects; 0.70 exactly is OK.
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       max_correlation_with_existing=0.70)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_correlation_missing_skips_check():
    # None means "not measured" — should not block.
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       max_correlation_with_existing=None)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


# ---------------- Phase A4: earnings blackout ----------------

def test_earnings_within_blackout_window_is_rejected():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       days_to_earnings=3)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("earnings" in f for f in result.failures)


def test_earnings_blackout_overridden_when_catalyst_is_earnings():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       days_to_earnings=2, catalyst_is_earnings=True)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_earnings_outside_window_is_allowed():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       days_to_earnings=10)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_earnings_at_boundary_is_allowed():
    # rule is "< 5" rejects; exactly 5 is OK.
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       days_to_earnings=5)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


# ---------------- Phase C: sector concentration cap ----------------

def test_sector_cap_blocks_third_position_in_same_sector():
    # Already 2 positions in this sector — adding another should be rejected.
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       open_positions_in_same_sector=2)
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("sector" in f for f in result.failures)


def test_sector_cap_allows_second_position_in_same_sector():
    # Cap is 2 → exactly 1 existing in sector means the candidate becomes #2 (allowed).
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       open_positions_in_same_sector=1)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_sector_cap_allows_first_position_in_sector():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       open_positions_in_same_sector=0)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_sector_cap_missing_skips_check():
    # None means "not measured" — should not block (production must populate this).
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       open_positions_in_same_sector=None)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


# ---------------- B3: reward-to-risk floor (audit 2026-06-03) ----------------

def test_rr_below_floor_is_rejected():
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       rr_at_entry=1.33)  # the original MU mislabel
    result = check_buy(baseline_account(), trade)
    assert not result.allowed
    assert any("R:R at entry" in f for f in result.failures)


def test_rr_at_floor_is_allowed():
    # rule is "< 2.0" rejects; exactly 2.0 is OK.
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       rr_at_entry=2.0)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_rr_above_floor_is_allowed():
    # A 15%-stop name still qualifies if cited upside makes R:R >= 2 (e.g. +35% PT).
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       rr_at_entry=2.33)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


def test_rr_missing_skips_check():
    # None means "not measured" — should not block (production must populate this).
    trade = ProposedBuy(symbol="AAPL", shares=100, ask_price=150.0,
                       catalyst_documented=True, is_stock=True,
                       rr_at_entry=None)
    result = check_buy(baseline_account(), trade)
    assert result.allowed, result.failures


