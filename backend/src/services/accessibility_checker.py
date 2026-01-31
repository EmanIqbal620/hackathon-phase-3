"""
Accessibility Testing Utilities
This module provides functions for checking and validating accessibility compliance.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
from ..models.accessibility import AccessibilitySettings
from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate
from ..database import sync_engine
from sqlmodel import Session, select
import re
import html
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WCAGLevel(Enum):
    """WCAG Conformance Levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class IssueSeverity(Enum):
    """Issue severity levels"""
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during testing"""
    id: str
    message: str
    element: Optional[str]
    severity: IssueSeverity
    wcag_conformance: List[str]
    guidance: str
    code_example: Optional[str] = None


@dataclass
class AccessibilityScanResult:
    """Result of an accessibility scan"""
    page_url: str
    scan_timestamp: datetime
    issues: List[AccessibilityIssue]
    summary: Dict[str, int]
    conformance_level: Optional[WCAGLevel]
    passed_rules: List[str]
    failed_rules: List[str]


class AccessibilityChecker:
    """Service class for performing accessibility checks and validation."""

    @staticmethod
    def check_color_contrast(foreground: str, background: str) -> Dict[str, Any]:
        """
        Check color contrast ratio between foreground and background colors.

        Args:
            foreground: Foreground color in hex format (#RRGGBB)
            background: Background color in hex format (#RRGGBB)

        Returns:
            Dictionary with contrast information and WCAG compliance status
        """
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c*2 for c in hex_color)
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def srgb_component(color: int) -> float:
            color = color / 255.0
            return color / 12.92 if color <= 0.03928 else pow((color + 0.055) / 1.055, 2.4)

        def relative_luminance(rgb: tuple) -> float:
            r, g, b = [srgb_component(c) for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        fg_rgb = hex_to_rgb(foreground)
        bg_rgb = hex_to_rgb(background)

        fg_lum = relative_luminance(fg_rgb)
        bg_lum = relative_luminance(bg_rgb)

        # Ensure higher value is first
        lighter = max(fg_lum, bg_lum)
        darker = min(fg_lum, bg_lum)

        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        contrast_ratio = round(contrast_ratio, 2)

        # WCAG 2.1 AA standards
        # Normal text: 4.5:1, Large text (18pt+ or 14pt+bold): 3:1
        # WCAG 2.1 AAA standards
        # Normal text: 7:1, Large text: 4.5:1
        is_aa_normal = contrast_ratio >= 4.5
        is_aa_large = contrast_ratio >= 3.0
        is_aaa_normal = contrast_ratio >= 7.0
        is_aaa_large = contrast_ratio >= 4.5

        return {
            "ratio": contrast_ratio,
            "wcag_aa_normal": is_aa_normal,
            "wcag_aa_large": is_aa_large,
            "wcag_aaa_normal": is_aaa_normal,
            "wcag_aaa_large": is_aaa_large,
            "recommended_action": "Increase contrast" if not is_aa_normal else "Good contrast",
            "foreground": foreground,
            "background": background
        }

    @staticmethod
    def check_alt_text(html_content: str) -> List[AccessibilityIssue]:
        """
        Check for missing alt text on images.

        Args:
            html_content: HTML content to scan

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Find all img tags
        img_pattern = r'<img[^>]*>'
        img_tags = re.findall(img_pattern, html_content, re.IGNORECASE)

        for img_tag in img_tags:
            # Check if alt attribute exists
            alt_match = re.search(r'alt=(["\'])(.*?)\1', img_tag, re.IGNORECASE)

            if not alt_match:
                # Missing alt attribute entirely
                issue = AccessibilityIssue(
                    id="missing-alt-attribute",
                    message="Image is missing alt attribute",
                    element=img_tag[:100] + "..." if len(img_tag) > 100 else img_tag,
                    severity=IssueSeverity.ERROR,
                    wcag_conformance=["1.1.1"],
                    guidance="Add descriptive alt text for all informative images. Use empty alt (alt=\"\") for decorative images.",
                    code_example='<img src="image.jpg" alt="Description of the image">'
                )
                issues.append(issue)
            else:
                # Check if alt text is empty or just whitespace
                alt_text = alt_match.group(2).strip()
                if not alt_text:
                    issue = AccessibilityIssue(
                        id="empty-alt-text",
                        message="Image has empty alt text",
                        element=img_tag[:100] + "..." if len(img_tag) > 100 else img_tag,
                        severity=IssueSeverity.WARNING,
                        wcag_conformance=["1.1.1"],
                        guidance="Provide meaningful alt text for informative images, or use empty alt for decorative images.",
                        code_example='<img src="image.jpg" alt="Description of the image">'
                    )
                    issues.append(issue)

        return issues

    @staticmethod
    def check_heading_structure(html_content: str) -> List[AccessibilityIssue]:
        """
        Check heading structure for proper hierarchy.

        Args:
            html_content: HTML content to scan

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Find all heading tags
        heading_pattern = r'<h([1-6]).*?>(.*?)</h\1>'
        headings = re.findall(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)

        if not headings:
            # No headings found
            issue = AccessibilityIssue(
                id="no-headings",
                message="No headings found in content",
                element=None,
                severity=IssueSeverity.WARNING,
                wcag_conformance=["1.3.1", "2.4.1"],
                guidance="Use proper heading structure (H1, H2, H3, etc.) to organize content hierarchically.",
                code_example='<h1>Main heading</h1><h2>Subheading</h2>'
            )
            issues.append(issue)
            return issues

        # Check for proper heading sequence
        last_level = 0
        for level_str, content in headings:
            level = int(level_str)

            # Check if heading level jumps more than one level
            if level > last_level + 1:
                content_preview = html.unescape(content)[:50].strip()
                if len(content) > 50:
                    content_preview += "..."

                issue = AccessibilityIssue(
                    id="skipped-heading-level",
                    message=f"Skipped heading level from H{last_level} to H{level}",
                    element=f"<h{level}>{content_preview}</h1>",
                    severity=IssueSeverity.WARNING,
                    wcag_conformance=["1.3.1", "2.4.6"],
                    guidance="Headings should only increase by one level at a time (e.g., H1 → H2, not H1 → H3).",
                    code_example=f'<h{last_level}>Previous heading</h{last_level}><h{level}>Current heading</h{level}>'
                )
                issues.append(issue)

            last_level = level

        return issues

    @staticmethod
    def check_form_labels(html_content: str) -> List[AccessibilityIssue]:
        """
        Check form controls for associated labels.

        Args:
            html_content: HTML content to scan

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Find all form inputs
        input_pattern = r'<input[^>]*>'
        inputs = re.findall(input_pattern, html_content, re.IGNORECASE)

        for input_tag in inputs:
            # Skip submit, reset, hidden inputs
            type_match = re.search(r'type=(["\'])([^"']*)\1', input_tag, re.IGNORECASE)
            input_type = type_match.group(2).lower() if type_match else "text"

            if input_type in ["submit", "reset", "hidden", "button"]:
                continue

            # Check for associated label
            has_label = False

            # Method 1: Label with 'for' attribute
            id_match = re.search(r'id=(["\'])([^"']*)\1', input_tag, re.IGNORECASE)
            if id_match:
                input_id = id_match.group(2)
                label_pattern = f'<label[^>]*for=(["\']){input_id}\\1[^>]*>'
                if re.search(label_pattern, html_content, re.IGNORECASE):
                    has_label = True

            # Method 2: Wrapped in label
            if not has_label:
                # Check if this input is wrapped inside a label
                label_wrapper_pattern = r'<label[^>]*>.*?' + re.escape(input_tag) + r'.*?</label>'
                if re.search(label_wrapper_pattern, html_content, re.IGNORECASE | re.DOTALL):
                    has_label = True

            if not has_label:
                issue = AccessibilityIssue(
                    id="missing-form-label",
                    message="Form input is missing associated label",
                    element=input_tag[:100] + "..." if len(input_tag) > 100 else input_tag,
                    severity=IssueSeverity.ERROR,
                    wcag_conformance=["1.3.1", "3.3.2"],
                    guidance="Associate all form controls with labels using either the 'for' attribute or by wrapping the input in a label.",
                    code_example='<label for="input-id">Label text</label><input id="input-id" type="text">'
                )
                issues.append(issue)

        return issues

    @staticmethod
    def check_link_text(html_content: str) -> List[AccessibilityIssue]:
        """
        Check link text for descriptiveness.

        Args:
            html_content: HTML content to scan

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Find all anchor tags
        link_pattern = r'<a[^>]*>(.*?)</a>'
        links = re.findall(link_pattern, html_content, re.IGNORECASE | re.DOTALL)

        for link_content in links:
            # Clean up the link text
            clean_text = html.unescape(link_content).strip()
            clean_text = re.sub(r'<[^>]+>', '', clean_text)  # Remove any nested HTML tags
            clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace

            # Check for non-descriptive link text
            non_descriptive_texts = [
                'click here', 'here', 'read more', 'more', 'learn more',
                'go', 'link', 'this', 'it', 'that', 'more...', '>>', '»'
            ]

            lower_text = clean_text.lower()
            if any(descriptive_text in lower_text for descriptive_text in non_descriptive_texts):
                issue = AccessibilityIssue(
                    id="non-descriptive-link",
                    message=f"Link text '{clean_text}' is not descriptive",
                    element=f"<a>{clean_text}</a>",
                    severity=IssueSeverity.WARNING,
                    wcag_conformance=["2.4.4", "2.4.9"],
                    guidance="Use descriptive link text that makes sense out of context. Avoid generic terms like 'click here' or 'read more'.",
                    code_example='<a href="/page">Visit our documentation page</a>'
                )
                issues.append(issue)

        return issues

    @staticmethod
    def check_keyboard_navigation(html_content: str) -> List[AccessibilityIssue]:
        """
        Check for keyboard navigation issues.

        Args:
            html_content: HTML content to scan

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Check for elements with negative tabindex
        negative_tabindex_pattern = r'tabindex=(["\']?)-?\d+(["\']?)'
        negative_matches = re.findall(negative_tabindex_pattern, html_content, re.IGNORECASE)
        if negative_matches:
            issue = AccessibilityIssue(
                id="negative-tabindex",
                message="Found elements with negative tabindex",
                element="Various elements",
                severity=IssueSeverity.WARNING,
                wcag_conformance=["2.1.1"],
                guidance="Avoid using negative tabindex values (-1) unless specifically hiding elements from keyboard navigation.",
                code_example='<button tabindex="0">Focusable button</button>'  # Positive example
            )
            issues.append(issue)

        # Check for focusable elements that might not be keyboard accessible
        focusable_elements_pattern = r'<(button|select|textarea|input)[^>]*>'
        focusable_elements = re.findall(focusable_elements_pattern, html_content, re.IGNORECASE)

        # Check for div/button without proper semantics
        div_button_pattern = r'<div[^>]*role=(["\'])button\1[^>]*>'
        div_buttons = re.findall(div_button_pattern, html_content, re.IGNORECASE)

        for _ in div_buttons:
            issue = AccessibilityIssue(
                id="div-as-button",
                message="Using div with button role instead of actual button element",
                element="<div role=\"button\">...",
                severity=IssueSeverity.WARNING,
                wcag_conformance=["4.1.2"],
                guidance="Use semantic HTML elements like <button> instead of divs with ARIA roles when possible.",
                code_example='<button type="button">Button text</button>'
            )
            issues.append(issue)

        return issues

    @staticmethod
    def scan_html_content(html_content: str, page_url: str = "") -> AccessibilityScanResult:
        """
        Perform a comprehensive accessibility scan of HTML content.

        Args:
            html_content: HTML content to scan
            page_url: URL of the page being scanned

        Returns:
            AccessibilityScanResult with issues and summary
        """
        start_time = datetime.utcnow()

        # Run all checks
        color_contrast_issues = []  # This would need CSS parsing
        alt_text_issues = AccessibilityChecker.check_alt_text(html_content)
        heading_issues = AccessibilityChecker.check_heading_structure(html_content)
        form_label_issues = AccessibilityChecker.check_form_labels(html_content)
        link_text_issues = AccessibilityChecker.check_link_text(html_content)
        keyboard_issues = AccessibilityChecker.check_keyboard_navigation(html_content)

        # Combine all issues
        all_issues = (
            alt_text_issues +
            heading_issues +
            form_label_issues +
            link_text_issues +
            keyboard_issues
        )

        # Create summary
        summary = {
            "total_issues": len(all_issues),
            "errors": len([i for i in all_issues if i.severity == IssueSeverity.ERROR]),
            "warnings": len([i for i in all_issues if i.severity == IssueSeverity.WARNING]),
            "notices": len([i for i in all_issues if i.severity == IssueSeverity.NOTICE])
        }

        # Determine conformance level based on issues
        conformance_level = None
        if summary["errors"] == 0 and summary["warnings"] == 0:
            conformance_level = WCAGLevel.AAA
        elif summary["errors"] == 0:
            conformance_level = WCAGLevel.AA
        else:
            conformance_level = WCAGLevel.A

        # Determine passed/failed rules
        all_rules = set()
        failed_rules = set()
        for issue in all_issues:
            for rule in issue.wcag_conformance:
                all_rules.add(rule)
                if issue.severity in [IssueSeverity.ERROR, IssueSeverity.WARNING]:
                    failed_rules.add(rule)
        passed_rules = list(all_rules - failed_rules)

        return AccessibilityScanResult(
            page_url=page_url,
            scan_timestamp=start_time,
            issues=all_issues,
            summary=summary,
            conformance_level=conformance_level,
            passed_rules=passed_rules,
            failed_rules=list(failed_rules)
        )

    @staticmethod
    def generate_accessibility_report(scan_results: AccessibilityScanResult) -> str:
        """
        Generate a human-readable accessibility report.

        Args:
            scan_results: Results from accessibility scan

        Returns:
            Formatted accessibility report
        """
        report_lines = [
            "=" * 60,
            "ACCESSIBILITY SCAN REPORT",
            "=" * 60,
            f"Page URL: {scan_results.page_url}",
            f"Scan Time: {scan_results.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Conformance Level: {scan_results.conformance_level.value if scan_results.conformance_level else 'Unknown'}",
            "",
            "SUMMARY:",
            "-" * 20,
            f"Total Issues: {scan_results.summary['total_issues']}",
            f"Errors: {scan_results.summary['errors']}",
            f"Warnings: {scan_results.summary['warnings']}",
            f"Notices: {scan_results.summary['notices']}",
            "",
            "DETAILED ISSUES:",
            "-" * 20
        ]

        for issue in scan_results.issues:
            severity_symbol = "❌" if issue.severity == IssueSeverity.ERROR else \
                            "⚠️" if issue.severity == IssueSeverity.WARNING else \
                            "ℹ️"
            report_lines.extend([
                f"{severity_symbol} {issue.message}",
                f"   WCAG: {', '.join(issue.wcag_conformance)}",
                f"   Guidance: {issue.guidance}",
                ""
            ])

        if scan_results.passed_rules:
            report_lines.extend([
                "PASSED RULES:",
                "-" * 20,
                ", ".join(scan_results.passed_rules),
                ""
            ])

        if scan_results.failed_rules:
            report_lines.extend([
                "FAILED RULES:",
                "-" * 20,
                ", ".join(scan_results.failed_rules),
                ""
            ])

        report_lines.extend([
            "RECOMMENDATIONS:",
            "-" * 20,
            "1. Address all errors immediately",
            "2. Review and fix warnings for better accessibility",
            "3. Consider notices for enhanced usability",
            "4. Retest after implementing fixes"
        ])

        return "\n".join(report_lines)

    @staticmethod
    def record_accessibility_metrics(user_id: str, scan_results: AccessibilityScanResult):
        """
        Record accessibility scan results as performance metrics.

        Args:
            user_id: ID of the user triggering the scan
            scan_results: Results from accessibility scan
        """
        with Session(sync_engine) as session:
            # Record total issues
            issues_metric = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type="accessibility_issues",
                value=scan_results.summary['total_issues'],
                unit="count",
                page_route=scan_results.page_url,
                additional_metadata={
                    "scan_timestamp": scan_results.scan_timestamp.isoformat(),
                    "conformance_level": scan_results.conformance_level.value if scan_results.conformance_level else None,
                    "breakdown": scan_results.summary
                }
            )
            issues_record = PerformanceMetrics.model_validate(issues_metric)
            session.add(issues_record)

            # Record conformance level
            if scan_results.conformance_level:
                conformance_metric = PerformanceMetricsCreate(
                    user_id=user_id,
                    metric_type="accessibility_conformance",
                    value=1 if scan_results.conformance_level == WCAGLevel.AA else 0.5 if scan_results.conformance_level == WCAGLevel.A else 0,
                    unit="level",
                    page_route=scan_results.page_url,
                    additional_metadata={
                        "level": scan_results.conformance_level.value,
                        "scan_timestamp": scan_results.scan_timestamp.isoformat()
                    }
                )
                conformance_record = PerformanceMetrics.model_validate(conformance_metric)
                session.add(conformance_record)

            session.commit()

    @staticmethod
    def validate_user_accessibility_settings(user_id: str, settings: Dict) -> List[str]:
        """
        Validate user accessibility settings.

        Args:
            user_id: ID of the user
            settings: Dictionary of accessibility settings to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Validate high contrast setting
        if "high_contrast_enabled" in settings:
            if not isinstance(settings["high_contrast_enabled"], bool):
                errors.append("high_contrast_enabled must be a boolean")

        # Validate reduced motion setting
        if "reduced_motion_enabled" in settings:
            if not isinstance(settings["reduced_motion_enabled"], bool):
                errors.append("reduced_motion_enabled must be a boolean")

        # Validate screen reader setting
        if "screen_reader_optimized" in settings:
            if not isinstance(settings["screen_reader_optimized"], bool):
                errors.append("screen_reader_optimized must be a boolean")

        # Validate font size preference
        if "font_size_preference" in settings:
            valid_sizes = ["small", "normal", "large", "extra_large"]
            if settings["font_size_preference"] not in valid_sizes:
                errors.append(f"font_size_preference must be one of {valid_sizes}")

        return errors