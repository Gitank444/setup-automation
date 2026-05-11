from dataclasses import dataclass
from config import MINIMUM_VERSION
from models import ToolStatus, ToolSignal


@dataclass
class ResolutionResult:
    status: ToolStatus
    reason: str
    suggestion: str | None = None
    details: dict | None = None


class ResolverAgent:
    def resolve(self, signal: ToolSignal) -> ResolutionResult:
        if not signal.binary_found:
            return ResolutionResult(
                status=ToolStatus.MISSING,
                reason='No executable was detected on the system.',
                suggestion='Install the missing tool or add it to PATH.'
            )

        if len(signal.all_locations) > 1:
            versions_set = set(
                loc.version for loc in signal.all_locations 
                if loc.version is not None
            )
            if len(versions_set) > 1:
                details = {
                    'locations': signal.all_locations,
                    'primary_path': signal.location,
                    'primary_version': signal.version
                }
                versions_str = ", ".join(sorted(versions_set))
                return ResolutionResult(
                    status=ToolStatus.CONFLICT,
                    reason=f"Multiple versions detected: {versions_str}",
                    suggestion="Keep only the version you intend to use. Remove others.",
                    details=details
                )

        if signal.broken:
            return ResolutionResult(
                status=ToolStatus.BROKEN,
                reason='A binary was detected but the tool cannot produce a valid version report.',
                suggestion='Repair or reinstall this tool from its vendor package.'
            )

        if signal.binary_found and not signal.path_found:
            return ResolutionResult(
                status=ToolStatus.PARTIAL,
                reason='The executable exists but it is not available through PATH.',
                suggestion=f'Add {signal.location} to PATH or reinstall using a package manager.',
                details={'path': signal.location}
            )

        if signal.version:
            minimum = MINIMUM_VERSION.get(signal.tool)
            if minimum and self._is_outdated(signal.version, minimum):
                return ResolutionResult(
                    status=ToolStatus.OUTDATED,
                    reason=f'Detected version {signal.version}, which is older than the required {minimum}.',
                    suggestion='Upgrade to the minimum supported version or later.',
                    details={'current': signal.version, 'required': minimum}
                )

        return ResolutionResult(
            status=ToolStatus.INSTALLED,
            reason='Tool is available and appears healthy.',
            suggestion=None
        )
        #9165536680

    def _normalize_version(self, version_text: str) -> tuple[int, ...]:
        import re
        numbers = re.findall(r'\d+', version_text)
        return tuple(int(part) for part in numbers) if numbers else ()

    def _is_outdated(self, current: str, minimum: str) -> bool:
        current_parts = self._normalize_version(current)
        minimum_parts = self._normalize_version(minimum)
        if not current_parts or not minimum_parts:
            return False
        length = max(len(current_parts), len(minimum_parts))
        current_parts += (0,) * (length - len(current_parts))
        minimum_parts += (0,) * (length - len(minimum_parts))
        return current_parts < minimum_parts


