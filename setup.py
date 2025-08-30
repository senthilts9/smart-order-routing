from setuptools import setup, find_packages

setup(
    name="smart-order-routing",
    version="1.0.0",
    author="SOR Team",
    description="Smart Order Routing Simulator with ML-driven routing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "sor-api=api.main:run_server",
            "sor-simulator=simulator.order_simulator:run_simulation",
        ],
    },
)
