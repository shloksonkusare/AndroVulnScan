# AndroVulnScan: Android Vulnerability Analysis Framework

## Overview
AndroVulnScan is a comprehensive static analysis framework designed to detect security vulnerabilities in Android applications. It provides a thorough security review of the app’s codebase, dependencies, and configurations, helping developers and security professionals identify potential vulnerabilities early in the development process. This solution strengthens Android application security, particularly for critical infrastructure like government, finance, and healthcare sectors.

## Problem Statement
As Android applications become more critical to sectors like government, finance, and healthcare, protecting these apps from security vulnerabilities is vital. Exploiting such vulnerabilities could lead to unauthorized access or disruption of essential services. To address this challenge, AndroVulnScan performs static analysis, combining manual and automated code reviews, configuration analysis, and dependency checks to ensure a thorough security assessment.

## Features
- **Static Code Analysis**: Identifies vulnerabilities such as SQL Injection, buffer overflow, and insecure API usage.
- **Configuration Analysis**: Ensures that Android apps follow secure configuration practices.
- **Third-party Dependency Scanning**: Analyzes external libraries and dependencies for known vulnerabilities.
- **Automated and Manual Review**: Offers a balanced approach by combining automation with manual code review to minimize false positives.
- **Customizable Rules**: Allows users to add custom rules for specific security needs.
- **Security Reports**: Provides detailed reports on identified vulnerabilities with recommendations for remediation.

## Architecture
The system is designed to integrate easily into Android application development pipelines. It supports continuous security analysis throughout the development process by automating static checks. AndroVulnScan uses the following tools:
- **MobSF**: For static code analysis and configuration checks.
- **Dependency-Check**: To evaluate third-party libraries and dependencies.

## Technical Stack
- **Programming Languages**: Python, Java, Kotlin
- **Tools for Static Code Analysis**: MobSF
- **Tools for Dependency Analysis**: Dependency-Check
- **Version Control**: Git
- **Configuration Tools**: StreamLit for dashboards

## Proof of Concept
A sample Android app was analyzed using MobSF for static code analysis and configuration assessment, along with Dependency-Check for evaluating third-party libraries. The results successfully identified critical vulnerabilities, including:
- SQL Injection
- Buffer Overflow
- Insecure API usage

This demonstrated the framework’s effectiveness in detecting and mitigating potential security risks.

## Impact & Benefits
- **Enhanced Security**: Reduces the risk of security breaches and attacks.
Developer Awareness: Encourages secure coding practices and educates developers on vulnerabilities.
- **Cost Savings**: Helps catch security issues early, reducing the cost of fixing them in production.
- **Social and Economic Benefits**: Safeguards user data and privacy, fostering trust in mobile applications.


## Installation and Setup

### Requirements:
1. Python version 3.10 - 3.11.
2. Node JS LTS version.
3. Java JDK LTS version.
4. Necessary Python Packages:
    - Pandas
    - Scikit-learn
    - Matplotlib
    - LangChain Grog
    - Pickle
    - Flask
    - ReportLab


### Steps to launch:
1. Clone the Repository
2. Running the Static Analysis section:
    1. Change the directory to the Static-Analysis.
    2. Run the following command:
        > .\setup.bat
    3. After setting up all the requirements, run the following command:
        > .\run.bat

    This will launch the static analysis section.
3. Running the Configuration Analysis section:
    1. Run the `feature_extraction.py` script.
    2. Run the `train_model.py` script.
    3. Run the `analyse.py` script.
    
    This will launch the configuration analysis section.
4. Running the External Dependencies Section:
    1. Run the `vulnerability.py` script.
    2. Run the following command in the terminal:
    > streamlit run vulnerabiity.py

    This will launch the external-dependencies section.
5. Launching the Project:
    1. Change the directory to the External-Dependencies.
    2. Run the following command (make sure to install node.js package in the machine):
    > npm start

*This will launch the complete project.*