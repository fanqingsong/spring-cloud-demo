#!/usr/bin/env python3
"""Move lesson 02-12 modules under spring-cloud-XX/ and add aggregator pom.xml."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LESSONS: dict[str, list[str]] = {
    "02": ["spring-cloud-02-consumer", "spring-cloud-02-provider", "spring-cloud-02-service"],
    "04": ["spring-cloud-04-consumer", "spring-cloud-04-provider", "spring-cloud-04-service"],
    "05": [
        "spring-cloud-05-consumer",
        "spring-cloud-05-provider",
        "spring-cloud-05-service",
        "spring-cloud-05-service-01",
        "spring-cloud-05-service-02",
        "spring-cloud-05-service-03",
    ],
    "06": [
        "spring-cloud-06-consumer",
        "spring-cloud-06-provider",
        "spring-cloud-06-provider-01",
        "spring-cloud-06-provider-02",
        "spring-cloud-06-provider-03",
        "spring-cloud-06-service",
    ],
    "08": [
        "spring-cloud-08-consumer",
        "spring-cloud-08-provider-01",
        "spring-cloud-08-provider-02",
        "spring-cloud-08-provider2-01",
        "spring-cloud-08-provider2-02",
        "spring-cloud-08-service",
    ],
    "09": [
        "spring-cloud-09-consumer",
        "spring-cloud-09-provider-01",
        "spring-cloud-09-provider-02",
        "spring-cloud-09-service",
    ],
    "10": [
        "spring-cloud-10-consumer",
        "spring-cloud-10-provider-01",
        "spring-cloud-10-provider-02",
        "spring-cloud-10-service",
    ],
    "11": [
        "spring-cloud-11-api",
        "spring-cloud-11-bean",
        "spring-cloud-11-consumer",
        "spring-cloud-11-provider-01",
        "spring-cloud-11-service",
    ],
    "12": [
        "spring-cloud-12-api",
        "spring-cloud-12-bean",
        "spring-cloud-12-consumer",
        "spring-cloud-12-provider-01",
        "spring-cloud-12-service",
    ],
}

CHAPTER_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
\txsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
\t<modelVersion>4.0.0</modelVersion>

\t<parent>
\t\t<groupId>com.roncoo.education</groupId>
\t\t<artifactId>spring-cloud-demo</artifactId>
\t\t<version>0.0.1-SNAPSHOT</version>
\t\t<relativePath>../pom.xml</relativePath>
\t</parent>

\t<artifactId>spring-cloud-{lesson}</artifactId>
\t<packaging>pom</packaging>
\t<name>spring-cloud-{lesson}</name>
\t<description>Spring Cloud 第 {lesson} 课</description>

\t<modules>
{modules}
\t</modules>

\t<properties>
\t\t<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
\t\t<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
\t\t<java.version>21</java.version>
\t</properties>
{dependency_management}
</project>
"""


def internal_artifacts(lesson: str, module_dirs: list[str]) -> list[str]:
    prefix = f"spring-cloud-{lesson}-"
    return [
        name
        for name in module_dirs
        if name.startswith(prefix) and (name.endswith("-bean") or name.endswith("-api"))
    ]


def fix_child_pom(pom: Path, lesson: str) -> None:
    text = pom.read_text(encoding="utf-8")
    artifact = pom.parent.name

    # Replace boot parent with chapter parent
    text = re.sub(
        r"\t<parent>\s*\n\t\t<groupId>org\.springframework\.boot</groupId>.*?</parent>\s*\n",
        f"""\t<parent>
\t\t<groupId>com.roncoo.education</groupId>
\t\t<artifactId>spring-cloud-{lesson}</artifactId>
\t\t<version>0.0.1-SNAPSHOT</version>
\t\t<relativePath>../pom.xml</relativePath>
\t</parent>

""",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # Remove duplicate coordinates before parent (old layout)
    text = re.sub(
        r"\n\t<groupId>com\.roncoo\.education</groupId>\n\t<artifactId>[^<]+</artifactId>\n\t<version>0\.0\.1-SNAPSHOT</version>\n",
        "\n",
        text,
        count=1,
    )

    if f"<artifactId>{artifact}</artifactId>" not in text.split("<parent>", 1)[0]:
        text = text.replace(
            "<modelVersion>4.0.0</modelVersion>\n\n",
            f"<modelVersion>4.0.0</modelVersion>\n\n\t<artifactId>{artifact}</artifactId>\n",
            1,
        )

    text = re.sub(r"\n\t<properties>.*?</properties>\n", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\n\t<dependencyManagement>.*?</dependencyManagement>\n", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\n\t<repositories>.*?</repositories>\n", "\n", text, flags=re.DOTALL)

    # Internal module deps without explicit version
    text = re.sub(
        r"(<artifactId>spring-cloud-" + lesson + r"-(?:bean|api)</artifactId>)\n\t\t\t<version>0\.0\.1-SNAPSHOT</version>\n",
        r"\1\n",
        text,
    )

    pom.write_text(text, encoding="utf-8")


def main() -> None:
    gitignore_src = ROOT / "spring-cloud-23" / ".gitignore"

    for lesson, modules in LESSONS.items():
        chapter_dir = ROOT / f"spring-cloud-{lesson}"
        chapter_dir.mkdir(exist_ok=True)

        if gitignore_src.exists() and not (chapter_dir / ".gitignore").exists():
            shutil.copy(gitignore_src, chapter_dir / ".gitignore")

        moved: list[str] = []
        for mod in modules:
            src = ROOT / mod
            dst = chapter_dir / mod
            if src.is_dir() and not dst.exists():
                shutil.move(str(src), str(dst))
                print(f"moved {mod} -> spring-cloud-{lesson}/")
            elif dst.is_dir():
                print(f"already in place: {mod}")
            else:
                print(f"WARN missing: {mod}")
                continue
            moved.append(mod)
            pom = dst / "pom.xml"
            if pom.exists():
                fix_child_pom(pom, lesson)

        module_lines = "\n".join(f"\t\t<module>{m}</module>" for m in moved)
        internal = internal_artifacts(lesson, moved)
        dep_mgmt = ""
        if internal:
            deps = "\n".join(
                f"""\t\t\t<dependency>
\t\t\t\t<groupId>com.roncoo.education</groupId>
\t\t\t\t<artifactId>{a}</artifactId>
\t\t\t\t<version>${{project.version}}</version>
\t\t\t</dependency>"""
                for a in internal
            )
            dep_mgmt = f"""
\t<dependencyManagement>
\t\t<dependencies>
{deps}
\t\t</dependencies>
\t</dependencyManagement>
"""

        chapter_pom = CHAPTER_POM.format(
            lesson=lesson, modules=module_lines, dependency_management=dep_mgmt
        )
        (chapter_dir / "pom.xml").write_text(chapter_pom, encoding="utf-8")
        print(f"written spring-cloud-{lesson}/pom.xml")


if __name__ == "__main__":
    main()
