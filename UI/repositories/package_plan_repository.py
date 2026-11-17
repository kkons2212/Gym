"""Repository operations for gym package plans."""

from __future__ import annotations

from typing import List, Optional, Type

from models.package_plan import PackagePlan
from repositories.base_repository import BaseRepository


class PackagePlanRepository(BaseRepository[PackagePlan]):
    """Read package plans offered by the gym."""

    table_name = "PackagePlan"
    id_column = "PlanId"

    @property
    def entity_type(self) -> Type[PackagePlan]:
        return PackagePlan

    def get_active_plans(self) -> List[PackagePlan]:
        """Fetch currently active package plans."""
        rows = self.execute_query(
            "SELECT * FROM `PackagePlan` WHERE `is_Active` = %s "
            "ORDER BY `PlanId` ASC",
            (1,),
        )
        return [PackagePlan.from_row(row) for row in rows]

    def get_by_id(self, plan_id: str) -> Optional[PackagePlan]:
        """Fetch a package plan by its identifier."""
        return super().get_by_id(plan_id)
