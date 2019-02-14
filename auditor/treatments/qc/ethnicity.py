from pkg_resources import resource_string

from auditor.agent import Agent
from auditor.trainers.site_visitor import SiteVisitor


def apply_caucasian_treatment(agent: Agent, count=1):
    agent.add_treatment("ethnicity", "caucasian")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.ethnicity', 'caucasian.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent


def apply_hispanic_treatment(agent: Agent, count=1):
    agent.add_treatment("ethnicity", "hispanic")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.ethnicity', 'hispanic.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent


def apply_afam_treatment(agent: Agent, count=1):
    agent.add_treatment("ethnicity", "african american")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.ethnicity', 'african_american.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent


def apply_asian_treatment(agent: Agent, count=1):
    agent.add_treatment("ethnicity", "asian")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.ethnicity', 'asian.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent
