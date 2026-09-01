def compare_metrics(reference,target,thresholds):
    rows=[]; failures=0
    for metric,rule in thresholds["metrics"].items():
        ref=reference.get(metric); tgt=target.get(metric); mandatory=bool(rule.get("mandatory",True))
        ttype=rule["type"]; threshold=rule["value"]; delta=None if ref is None or tgt is None else tgt-ref
        if tgt is None: verdict="INCONCLUSIVE"
        elif ttype=="min_delta": verdict="PASS" if delta is not None and delta>=threshold else "FAIL"
        elif ttype=="min_value": verdict="PASS" if tgt>=threshold else "FAIL"
        elif ttype=="max_value": verdict="PASS" if tgt<=threshold else "FAIL"
        elif ttype=="zero_regression": verdict="PASS" if delta is not None and delta>=0 else "FAIL"
        elif ttype=="min_ci_lower":
            lower=target.get("confidence_intervals",{}).get(metric,{}).get("lower")
            verdict="PASS" if lower is not None and lower>=threshold else "FAIL"
        else: verdict="CHECK"
        if mandatory and verdict in {"FAIL","INCONCLUSIVE"}: failures+=1
        rows.append({"metric":metric,"reference":ref,"target":tgt,"delta":delta,"threshold_type":ttype,
                     "threshold":threshold,"mandatory":mandatory,"verdict":verdict,
                     "target_ci":target.get("confidence_intervals",{}).get(metric)})
    return rows,{"mandatory_metric_failures":failures,"overall_verdict":"FAIL" if failures else "PASS / REVIEW NON-MANDATORY"}
