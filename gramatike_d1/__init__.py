# gramatike_d1/__init__.py
# Módulo de banco de dados D1 para Cloudflare Workers
# Este módulo contém todas as funções para o backend serverless
#
# NOTA: Renomeado de 'workers/' para 'gramatike_d1/' para evitar conflito
# com o módulo 'workers' built-in do Cloudflare Workers Python.

from .db import *
from .auth import *
