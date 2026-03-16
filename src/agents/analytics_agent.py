"""Analytics collection and aggregation agent."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from src.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AnalyticsAgent(BaseAgent):
    """Collects and aggregates analytics data for creators."""

    def __init__(self):
        super().__init__("AnalyticsAgent")

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect or aggregate analytics.

        task types:
        - "aggregate": aggregate metrics for a creator over a period
        - "trends": calculate engagement trends

        task = {
            "task_type": "aggregate" | "trends",
            "creator_id": "...",
            "period": "7d" | "30d" | "90d",
            "metrics": [...],
        }
        """
        task_type = task.get("task_type", "aggregate")
        creator_id = task.get("creator_id")

        if not creator_id:
            return {"error": "creator_id is required"}

        if task_type == "aggregate":
            return await self._aggregate_metrics(task)
        elif task_type == "trends":
            return await self._calculate_trends(task)
        else:
            return {"error": f"Unknown task_type: {task_type}"}

    async def _aggregate_metrics(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate metrics for a creator over a period."""
        creator_id = task.get("creator_id")
        period = task.get("period", "30d")
        requested_metrics = task.get(
            "metrics", ["likes", "comments", "views", "shares", "subscribers"]
        )

        period_days = self._parse_period(period)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        # Fetch metrics from database
        metrics_data = await self._fetch_metrics_from_db(
            creator_id, start_date, end_date, requested_metrics
        )

        # Calculate engagement rate
        total_views = metrics_data.get("views", 0)
        total_interactions = (
            metrics_data.get("likes", 0)
            + metrics_data.get("comments", 0)
            + metrics_data.get("shares", 0)
        )
        engagement_rate = (
            (total_interactions / total_views * 100) if total_views > 0 else 0.0
        )

        # Identify top content
        top_content = await self._get_top_content(creator_id, start_date, end_date)

        # Calculate daily averages
        daily_averages = {}
        for metric in requested_metrics:
            total = metrics_data.get(metric, 0)
            daily_averages[f"{metric}_per_day"] = (
                round(total / period_days, 2) if period_days > 0 else 0
            )

        return {
            "creator_id": creator_id,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics": metrics_data,
            "engagement_rate": round(engagement_rate, 2),
            "daily_averages": daily_averages,
            "top_content": top_content,
        }

    async def _calculate_trends(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate engagement trends for a creator."""
        creator_id = task.get("creator_id")
        period = task.get("period", "30d")

        period_days = self._parse_period(period)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        # Fetch daily metrics from database
        daily_data = await self._fetch_daily_metrics_from_db(
            creator_id, start_date, end_date
        )

        if not daily_data:
            return {
                "creator_id": creator_id,
                "period": period,
                "trends": {},
                "message": "No data available for the specified period",
            }

        # Calculate trends for each metric
        trends = {}
        metric_totals = defaultdict(list)

        for day_record in daily_data:
            for metric, value in day_record.get("metrics", {}).items():
                metric_totals[metric].append(value)

        for metric, values in metric_totals.items():
            trend = self._compute_trend_direction(values)
            change_pct = self._compute_change_percentage(values)
            trends[metric] = {
                "direction": trend,
                "change_percent": change_pct,
                "current_value": values[-1] if values else 0,
                "average": round(sum(values) / len(values), 2) if values else 0,
                "peak": max(values) if values else 0,
                "data_points": len(values),
            }

        # Identify best performing day
        best_day = None
        best_score = 0
        for day_record in daily_data:
            score = sum(day_record.get("metrics", {}).values())
            if score > best_score:
                best_score = score
                best_day = day_record.get("date")

        return {
            "creator_id": creator_id,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "trends": trends,
            "best_day": best_day,
            "total_data_points": len(daily_data),
        }

    def _parse_period(self, period: str) -> int:
        """Parse period string to number of days."""
        period_map = {
            "7d": 7,
            "1w": 7,
            "30d": 30,
            "1m": 30,
            "90d": 90,
            "3m": 90,
            "365d": 365,
            "1y": 365,
        }
        return period_map.get(period, 30)

    def _compute_trend_direction(self, values: List[float]) -> str:
        """Compute whether a metric is trending up, down, or stable."""
        if len(values) < 2:
            return "stable"

        # Compare first half average to second half average
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(values[mid:]) / (len(values) - mid)

        if first_half_avg == 0:
            return "up" if second_half_avg > 0 else "stable"

        change = (second_half_avg - first_half_avg) / first_half_avg

        if change > 0.05:
            return "up"
        elif change < -0.05:
            return "down"
        return "stable"

    def _compute_change_percentage(self, values: List[float]) -> float:
        """Compute percentage change from first to last value."""
        if len(values) < 2:
            return 0.0

        first = values[0]
        last = values[-1]

        if first == 0:
            return 100.0 if last > 0 else 0.0

        return round((last - first) / first * 100, 2)

    async def _fetch_metrics_from_db(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str],
    ) -> Dict[str, int]:
        """Fetch aggregated metrics from the database."""
        try:
            from src.core.database import Database

            db = Database()
            results = {}

            for metric in metrics:
                query = """
                    SELECT COALESCE(SUM(value), 0) as total
                    FROM analytics_events
                    WHERE creator_id = ?
                    AND metric_type = ?
                    AND created_at >= ?
                    AND created_at <= ?
                """
                db.cursor.execute(
                    query,
                    (
                        creator_id,
                        metric,
                        start_date.isoformat(),
                        end_date.isoformat(),
                    ),
                )
                row = db.cursor.fetchone()
                results[metric] = row[0] if row else 0

            db.conn.close()
            return results

        except Exception as e:
            logger.warning(f"Could not fetch metrics from DB: {e}")
            # Return empty metrics if DB not available
            return {metric: 0 for metric in metrics}

    async def _get_top_content(
        self, creator_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get top performing content for a creator."""
        try:
            from src.core.database import Database

            db = Database()

            query = """
                SELECT content_id, content_type, title,
                       COALESCE(SUM(CASE WHEN metric_type = 'views' THEN value END), 0) as views,
                       COALESCE(SUM(CASE WHEN metric_type = 'likes' THEN value END), 0) as likes,
                       COALESCE(SUM(CASE WHEN metric_type = 'comments' THEN value END), 0) as comments
                FROM analytics_events
                WHERE creator_id = ?
                AND created_at >= ?
                AND created_at <= ?
                GROUP BY content_id
                ORDER BY views DESC
                LIMIT 5
            """
            db.cursor.execute(
                query,
                (creator_id, start_date.isoformat(), end_date.isoformat()),
            )
            rows = db.cursor.fetchall()

            top_content = []
            for row in rows:
                top_content.append(
                    {
                        "content_id": row[0],
                        "content_type": row[1],
                        "title": row[2],
                        "views": row[3],
                        "likes": row[4],
                        "comments": row[5],
                    }
                )

            db.conn.close()
            return top_content

        except Exception as e:
            logger.warning(f"Could not fetch top content from DB: {e}")
            return []

    async def _fetch_daily_metrics_from_db(
        self, creator_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch daily metrics from the database."""
        try:
            from src.core.database import Database

            db = Database()

            query = """
                SELECT DATE(created_at) as day, metric_type, SUM(value) as total
                FROM analytics_events
                WHERE creator_id = ?
                AND created_at >= ?
                AND created_at <= ?
                GROUP BY DATE(created_at), metric_type
                ORDER BY day ASC
            """
            db.cursor.execute(
                query,
                (creator_id, start_date.isoformat(), end_date.isoformat()),
            )
            rows = db.cursor.fetchall()

            # Group by date
            daily_map = defaultdict(dict)
            for row in rows:
                day = row[0]
                metric_type = row[1]
                total = row[2]
                daily_map[day][metric_type] = total

            daily_data = [
                {"date": day, "metrics": metrics}
                for day, metrics in sorted(daily_map.items())
            ]

            db.conn.close()
            return daily_data

        except Exception as e:
            logger.warning(f"Could not fetch daily metrics from DB: {e}")
            return []
