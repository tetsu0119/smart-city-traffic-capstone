SELECT COUNT(*)
FROM Metro_Interstate_Traffic_Volume;

-- Task 1.2: Annual traffic trends (2012-2017)
SELECT
    strftime('%Y', date_time) AS year,
    SUM(traffic_volume) AS total_traffic_volume
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
GROUP BY strftime('%Y', date_time)
ORDER BY year;

-- Task 1.2: Annual traffic volume with observation coverage
SELECT
    strftime('%Y', date_time) AS year,
    COUNT(*) AS hour_rows,
    SUM(traffic_volume) AS total_traffic_volume,
    ROUND(AVG(traffic_volume), 2) AS avg_hourly_traffic
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
GROUP BY strftime('%Y', date_time)
ORDER BY year;

-- Task 1.2: Check observation date coverage by year
SELECT
    strftime('%Y', date_time) AS year,
    MIN(date_time) AS first_observation,
    MAX(date_time) AS last_observation,
    COUNT(*) AS hour_rows
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
GROUP BY strftime('%Y', date_time)
ORDER BY year;

-- Task 1.2: Year-on-year changes in total and average traffic
WITH yearly_traffic AS (
    SELECT
        CAST(strftime('%Y', date_time) AS INTEGER) AS year,
        COUNT(*) AS hour_rows,
        SUM(traffic_volume) AS total_traffic_volume,
        AVG(traffic_volume) AS avg_hourly_traffic
    FROM Metro_Interstate_Traffic_Volume
    WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
    GROUP BY strftime('%Y', date_time)
)
SELECT
    year,
    hour_rows,
    total_traffic_volume,
    total_traffic_volume - LAG(total_traffic_volume)
        OVER (ORDER BY year) AS total_change,
    ROUND(avg_hourly_traffic, 2) AS avg_hourly_traffic,
    ROUND(
        avg_hourly_traffic - LAG(avg_hourly_traffic)
        OVER (ORDER BY year), 2
    ) AS avg_hourly_change
FROM yearly_traffic
ORDER BY year;

-- Task 1.3: Check holiday records for New Year's Day and Labor Day
SELECT
    strftime('%Y', date_time) AS year,
    holiday,
    COUNT(*) AS record_count
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2015' AND '2017'
  AND holiday IN ('New Years Day', 'Labor Day')
GROUP BY strftime('%Y', date_time), holiday
ORDER BY year, holiday;

-- Task 1.3: Temperature and traffic around holidays
SELECT
    strftime('%Y', date_time) AS year,
    holiday,
    COUNT(*) AS record_count,
    ROUND(AVG(temp), 2) AS avg_temp_kelvin,
    ROUND(AVG(temp) - 273.15, 2) AS avg_temp_celsius,
    ROUND(AVG(traffic_volume), 2) AS avg_traffic_volume
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2015' AND '2017'
  AND holiday IN ('New Years Day', 'Labor Day')
GROUP BY strftime('%Y', date_time), holiday
ORDER BY year, holiday;

-- Task 2.1: Basic descriptive statistics for traffic volume
SELECT
    ROUND(AVG(traffic_volume), 2) AS mean_traffic_volume,
    MIN(traffic_volume) AS minimum_traffic_volume,
    MAX(traffic_volume) AS maximum_traffic_volume,
    MAX(traffic_volume) - MIN(traffic_volume) AS traffic_volume_range
FROM Metro_Interstate_Traffic_Volume;

-- Task 2.1: Median traffic volume
SELECT ROUND(AVG(traffic_volume), 2) AS median_traffic_volume
FROM (
    SELECT traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    ORDER BY traffic_volume
    LIMIT 2 - (SELECT COUNT(*) FROM Metro_Interstate_Traffic_Volume) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM Metro_Interstate_Traffic_Volume)
);

-- Task 2.1: Variance and standard deviation of traffic volume
SELECT
    ROUND(
        AVG(traffic_volume * traffic_volume)
        - AVG(traffic_volume) * AVG(traffic_volume),
        2
    ) AS variance_traffic_volume,

    ROUND(
        SQRT(
            AVG(traffic_volume * traffic_volume)
            - AVG(traffic_volume) * AVG(traffic_volume)
        ),
        2
    ) AS stddev_traffic_volume
FROM Metro_Interstate_Traffic_Volume;

-- Task 2.2: Correlation between temperature and traffic volume
SELECT
    ROUND(
        (
            AVG(temp * traffic_volume)
            - AVG(temp) * AVG(traffic_volume)
        )
        /
        (
            SQRT(AVG(temp * temp) - AVG(temp) * AVG(temp))
            *
            SQRT(
                AVG(traffic_volume * traffic_volume)
                - AVG(traffic_volume) * AVG(traffic_volume)
            )
        ),
        4
    ) AS correlation_temp_traffic
FROM Metro_Interstate_Traffic_Volume;

-- Task 2.2: Pearson Correlation Between Temperature and Traffic Volume
-- Excluding Invalid Temperature Values (0 K)
WITH pairs AS (
    SELECT temp, traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    WHERE temp IS NOT NULL
      AND traffic_volume IS NOT NULL
      AND temp > 0                       -- 0K の異常値を除く
),
agg AS (
    SELECT
        COUNT(*) AS n,
        SUM(temp) AS sum_x,
        SUM(traffic_volume) AS sum_y,
        SUM(temp * traffic_volume) AS sum_xy,
        SUM(temp * temp) AS sum_x2,
        SUM(traffic_volume * traffic_volume) AS sum_y2
    FROM pairs
)
SELECT
    ROUND(
        (n * sum_xy - sum_x * sum_y)
        / SQRT(
            (n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)
          ),
        4
    ) AS correlation_temp_volume
FROM agg;


-- Task 3.1: Basic probability
-- Congestion = traffic_volume > 5500
-- Clear weather = weather_main = 'Clear'

SELECT
    COUNT(*) AS total_records,

    SUM(CASE WHEN traffic_volume > 5500 THEN 1 ELSE 0 END)
        AS congestion_records,
    ROUND(
        AVG(CASE WHEN traffic_volume > 5500 THEN 1.0 ELSE 0 END),
        4
    ) AS p_congestion,

    SUM(CASE WHEN weather_main = 'Clear' THEN 1 ELSE 0 END)
        AS clear_weather_records,
    ROUND(
        AVG(CASE WHEN weather_main = 'Clear' THEN 1.0 ELSE 0 END),
        4
    ) AS p_clear_weather,

    SUM(CASE
        WHEN traffic_volume > 5500 AND weather_main = 'Clear' THEN 1
        ELSE 0
    END) AS congestion_and_clear_records,
    ROUND(
        AVG(CASE
            WHEN traffic_volume > 5500 AND weather_main = 'Clear' THEN 1.0
            ELSE 0
        END),
        4
    ) AS p_congestion_and_clear
FROM Metro_Interstate_Traffic_Volume;

-- Task 3.2: Conditional probability, independence and odds ratio
-- Congestion = traffic_volume > 5500
-- Clear = weather_main 'Clear'; cloudy = weather_main 'Clouds'
-- High temperature = temp > 292K

WITH flags AS (
    SELECT
        CASE WHEN traffic_volume > 5500 THEN 1 ELSE 0 END AS is_congestion,
        CASE WHEN weather_main = 'Clear' THEN 1 ELSE 0 END AS is_clear,
        CASE WHEN weather_main = 'Clouds' THEN 1 ELSE 0 END AS is_cloudy,
        CASE WHEN temp > 292 THEN 1 ELSE 0 END AS is_high_temp
    FROM Metro_Interstate_Traffic_Volume
    WHERE traffic_volume IS NOT NULL
      AND weather_main IS NOT NULL
      AND temp IS NOT NULL
),
counts AS (
    SELECT
        COUNT(*) AS n,
        SUM(is_congestion) AS congestion_n,
        SUM(is_clear) AS clear_n,
        SUM(is_congestion * is_clear) AS congestion_and_clear_n,
        SUM(is_congestion * is_high_temp) AS congestion_and_hot_n,
        SUM(CASE
            WHEN is_clear = 1 AND is_congestion = 0 THEN 1
            ELSE 0
        END) AS clear_not_congestion_n,
        SUM(CASE
            WHEN is_cloudy = 1 AND is_congestion = 1 THEN 1
            ELSE 0
        END) AS cloudy_congestion_n,
        SUM(CASE
            WHEN is_cloudy = 1 AND is_congestion = 0 THEN 1
            ELSE 0
        END) AS cloudy_not_congestion_n
    FROM flags
)
SELECT
    -- P(Clear Weather | Congestion)
    ROUND(1.0 * congestion_and_clear_n / congestion_n, 4)
        AS p_clear_given_congestion,

    -- P(High Temperature | Congestion)
    ROUND(1.0 * congestion_and_hot_n / congestion_n, 4)
        AS p_high_temp_given_congestion,

    -- Observed P(Congestion AND Clear)
    ROUND(1.0 * congestion_and_clear_n / n, 4)
        AS p_congestion_and_clear,

    -- Expected joint probability if independent: P(A) x P(B)
    ROUND((1.0 * congestion_n / n) * (1.0 * clear_n / n), 4)
        AS p_if_independent,

    -- Odds ratio: congestion odds in clear weather / congestion odds in cloudy weather
    ROUND(
        (1.0 * congestion_and_clear_n / clear_not_congestion_n)
        / (1.0 * cloudy_congestion_n / cloudy_not_congestion_n),
        4
    ) AS odds_ratio_clear_vs_cloudy
FROM counts;

-- Data quality check: invalid zero-Kelvin temperature records
SELECT COUNT(*) AS zero_kelvin_records
FROM Metro_Interstate_Traffic_Volume
WHERE temp = 0;