from pkg_resources import resource_string

from auditor.agent import Agent
from auditor.trainers.site_visitor import SiteVisitor


def apply_control_treatment(agent: Agent, count=1):
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites', 'control.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent


def apply_caucasian_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("ethnicity", "caucasian")
        agent.training_steps.append(SiteVisitor(['https://foxnews.com']))
    return agent


def apply_hispanic_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("ethnicity", "hispanic")
        agent.training_steps.append(SiteVisitor(['https://univision.com']))
    return agent


def apply_afam_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("ethnicity", "african-american")
        agent.training_steps.append(SiteVisitor(['https://theroot.com']))
    return agent


def apply_asian_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("ethnicity", "asian")
        agent.training_steps.append(SiteVisitor(['https://theroot.com']))
    return agent


def apply_female_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("gender", "female")
        agent.training_steps.append(SiteVisitor(['https://zulily.com']))
    return agent


def apply_male_treatment(agent: Agent, count=1):
    for i in range(count):
        agent.add_treatment("gender", "male")
        agent.training_steps.append(SiteVisitor(['https://newarena.com']))
    return agent
