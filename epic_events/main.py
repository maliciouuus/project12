#!/usr/bin/env python3
"""
Point d'entrée principal de l'application Epic Events CRM.
"""
import os
import click
import sentry_sdk
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

@click.group()
def cli():
    """Epic Events CRM - Système de gestion de la relation client."""
    pass

@cli.command()
def version():
    """Affiche la version de l'application."""
    click.echo("Epic Events CRM v0.1.0")

if __name__ == "__main__":
    cli() 