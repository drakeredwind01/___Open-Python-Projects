# Correlation Findings — data.csv

| Pair | Pearson r | Lag | Meaning |
|---|---|---|---|
| Sales ↔ Website_Traffic | 0.998 | 0 | Near-perfect, move together with no delay |
| Sales ↔ Temperature_F | 0.405 | -5 months | Temperature leads Sales by 5 months |
| Temperature_F ↔ Website_Traffic | 0.403 | +5 months | Indirect — inherited from Sales relationship |

**Key takeaways:**
- Sales and Website_Traffic are the clean demo pair — almost perfectly correlated.
- The Temperature → Sales lag of 5 months is the interesting one: warmer weather drives sales, but with a delay.
