# Setup counts behind the per-ASN cells of T1, T4 and T5 (6 Oct 2026)

Decision (Hannah, 6 Oct 2026): verdicts are per probe ASN only, all-Russia is description, and every per-ASN cell states how many distinct setups it rests on.

`setup_counts.py` recomputes, from the derived stage tables already on disk (no new pull), the measurements behind each per-ASN cell and counts:

- `setups`: distinct (software_name, software_version, test_version). The derived tables carry no platform, engine or origin annotations, so this key is coarser than the one in `AS39028/as39028-characterisation-2026-10-06.md`; many devices can share one setup. It is a lower bound on distinct devices.
- `reports`: distinct report_id. Unattended apps submit one report per measurement or per short batch, so this is an upper bound on devices, often far above it.
- `setups_with_fail`, `reports_with_fail`, `top_setup_share_of_fails`: the same, among the measurements in the cell's failure family (T1: netfail; T4 E1: blocked; T4 E2 and T5: stall).

Filters reproduce the docs' cells: control-ok, non-mobile, https strict inputs (T4/T5), set F and the 14:05–14:25 UTC core window (T1). The control-ok n in every row matches the n printed in the result docs for the cells checked (AS50716 Hetzner after 174; AS12389 Cloudflare large after 1,673; AS12389 T1 event 29).

Output: `setup_counts.csv` (244 rows).
