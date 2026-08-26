""""""

__all__ = []

import json


my_thing = {}

other = {
    "start_index": 0,
    "length": len(token),
    "message": (
        "Compound statement chains (if/elif/else, try/except/finally) should have no blank lines between parts, "
        "except after return/yield/exit statements."
    )
}
end = (
    line_offsets[container_node.end_lineno - 1]
    + container_node.end_col_offset
    - 1
)
end = (
    line_offsets[container_node.end_lineno - 1]
    + container_node.end_col_offset
    - 120
)


class MyClass:


    def _build_punc_tree(self, nodes: list):
        """Build parent-child relationships among paired punc nodes."""
        sorted_nodes = sorted(
            nodes,
            key=lambda n: (n['_flat_start'], -n['_flat_end'], n['some_really_long_key_here_and_there'])
        )
        for n in shallowest_first:
            if n['_expand'] and n['_children']:
                if n['type'] not in (
                    "list",
                    "set",
                    "dict",
                    "tuple"
                ):
                    continue


    def _is_dict_subscript(self, node: ast.Subscript) -> bool:
        if isinstance(node.slice, ast.Tuple):
            return False

        if isinstance(node.value, ast.Name):
            name = node.value.id
            if (
                name[0].isupper()
                or name in (
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "frozenset",
                    "type"
                )
            ):
                return False

        else:
            if top_level_lines:
                ops_correct = all(line.startswith(f"{op_str} ") for line in top_level_lines[1:])

        if not op_texts or len(op_texts) != len(operands):
            if (
                not is_if_context
                and not is_assign_context
                and not is_return_context
            ):
                return flat if not should_expand else current_text

        else:
            if len(string_char) == 3 and line[i:i + 3] == string_char:
                in_string = False
                result.append(line[i:i + 3])
                i += 3
                continue
            elif (
                len(string_char) == 1
                and ch == string_char
                and self._is_closing_quote(line, i)
            ):
                in_string = False

            result.append(ch)


def test_validate_grant_invalid(authz):
    result = asyncio.run(
        authz.validate_grant(
            {
                "effect": "bad"
            }
        )
    )


class PythonCompoundChainFormatter(Formatter):
    """Format blank lines between parts of compound statement chains.

    Rules:
    - Between compound parts (if→elif, try→except, etc.): no blank line
    - Exception: after return/yield/exit → 1 blank line
    - Exception: after a compound statement (if/for/while/with/try) as
    the last statement → 1 blank line

    Examples
    --------

    ```python
    from cleer import PythonCompoundChainFormatter

    formatter = PythonCompoundChainFormatter()
    result = formatter.format("if x:\\n    pass\\n\\nelse:\\n    pass\\n")
    ```
    """
    accepts_token_types = ["python_compound_chain"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect compound chain for incorrect blank lines.

        Parameters
        ----------
        token : str
            Token containing the full compound chain.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if blank lines are correct.
        """
        formatted = self.format(token)

        if formatted != token:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": (
                        "Compound statement chains (if/elif/else, try/except/finally) should have no blank lines between parts, "
                        "except after return/yield/exit statements."
                    )
                }
            ]

        return []


default_config: AuthzeeConfig = {
    "authzee": {
        "raise_errors": True
    },
    "start": {
        "compute_start": {
            "storage": {}
        },
        "storage_start": {}
    },
    "shutdown": {
        "compute_shutdown": {
            "storage": {}
        },
        "storage_shutdown": {}
    },
    "construct": {
        "compute_construct": {},
        "storage_construct": {}
    },
    "destroy": {
        "compute_destroy": {},
        "storage_destroy": {}
    },
    "validate_context_def": {},
    "list_context_defs": {
        "page_size": 100,
        "use_cache": False
    },
    "get_context_def": {
        "use_cache": False
    },
    "put_context_def": {},
    "delete_context_def": {},
    "validate_identity_def": {},
    "list_identity_defs": {
        "page_size": 100,
        "use_cache": False
    },
    "get_identity_def": {
        "use_cache": False
    },
    "put_identity_def": {},
    "delete_identity_def": {},
    "validate_resource_def": {},
    "list_resource_defs": {
        "page_size": 100,
        "use_cache": False
    },
    "get_resource_def": {
        "use_cache": False
    },
    "put_resource_def": {},
    "delete_resource_def": {},
    "validate_grant": {},
    "list_grants": {
        "page_size": 100,
        "use_cache": False
    },
    "get_grant": {
        "use_cache": False
    },
    "enact": {},
    "repeal": {},
    "list_grant_refs": {
        "page_size": 10,
        "use_cache": False
    },
    "cleanup_latches": {},
    "validate_request": {
        "get_context_def": {
            "use_cache": True
        },
        "use_list_context_defs": True,
        "list_context_defs": {
            "page_size": 100,
            "use_cache": True
        },
        "get_identity_def": {
            "use_cache": True
        },
        "use_list_identity_defs": True,
        "list_identity_defs": {
            "page_size": 100,
            "use_cache": True
        },
        "get_resource_def": {
            "use_cache": True
        },
        "use_list_resource_defs": True,
        "list_resource_defs": {
            "page_size": 100,
            "use_cache": True
        }
    },
    "validate_batch_request": {
        "get_context_def": {
            "use_cache": True
        },
        "use_list_context_defs": True,
        "list_context_defs": {
            "page_size": 100,
            "use_cache": True
        },
        "get_identity_def": {
            "use_cache": True
        },
        "use_list_identity_defs": True,
        "list_identity_defs": {
            "page_size": 100,
            "use_cache": True
        },
        "get_resource_def": {
            "use_cache": True
        },
        "use_list_resource_defs": True,
        "list_resource_defs": {
            "page_size": 100,
            "use_cache": True
        }
    },
    "audit": {
        "validate_request": {
            "get_context_def": {
                "use_cache": True
            },
            "use_list_context_defs": True,
            "list_context_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_identity_def": {
                "use_cache": True
            },
            "use_list_identity_defs": True,
            "list_identity_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_resource_def": {
                "use_cache": True
            },
            "use_list_resource_defs": True,
            "list_resource_defs": {
                "page_size": 100,
                "use_cache": True
            }
        },
        "list_grants": {
            "page_size": 100,
            "use_cache": True
        }
    },
    "batch_audit": {
        "validate_batch_request": {
            "get_context_def": {
                "use_cache": True
            },
            "use_list_context_defs": True,
            "list_context_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_identity_def": {
                "use_cache": True
            },
            "use_list_identity_defs": True,
            "list_identity_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_resource_def": {
                "use_cache": True
            },
            "use_list_resource_defs": True,
            "list_resource_defs": {
                "page_size": 100,
                "use_cache": True
            }
        },
        "list_grants": {
            "page_size": 100,
            "use_cache": True
        }
    },
    "authorize": {
        "validate_request": {
            "get_context_def": {
                "use_cache": True
            },
            "use_list_context_defs": True,
            "list_context_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_identity_def": {
                "use_cache": True
            },
            "use_list_identity_defs": True,
            "list_identity_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_resource_def": {
                "use_cache": True
            },
            "use_list_resource_defs": True,
            "list_resource_defs": {
                "page_size": 100,
                "use_cache": True
            }
        },
        "list_grants": {
            "page_size": 100,
            "use_cache": True
        },
        "parallel_paging": True,
        "list_grant_refs": {
            "page_size": 10,
            "use_cache": True
        }
    },
    "batch_authorize": {
        "validate_batch_request": {
            "get_context_def": {
                "use_cache": True
            },
            "use_list_context_defs": True,
            "list_context_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_identity_def": {
                "use_cache": True
            },
            "use_list_identity_defs": True,
            "list_identity_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_resource_def": {
                "use_cache": True
            },
            "use_list_resource_defs": True,
            "list_resource_defs": {
                "page_size": 100,
                "use_cache": True
            }
        },
        "validate_request": {
            "get_context_def": {
                "use_cache": True
            },
            "use_list_context_defs": True,
            "list_context_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_identity_def": {
                "use_cache": True
            },
            "use_list_identity_defs": True,
            "list_identity_defs": {
                "page_size": 100,
                "use_cache": True
            },
            "get_resource_def": {
                "use_cache": True
            },
            "use_list_resource_defs": True,
            "list_resource_defs": {
                "page_size": 100,
                "use_cache": True
            }
        },
        "list_grants": {
            "page_size": 100,
            "use_cache": True
        },
        "parallel_paging": True,
        "list_grant_refs": {
            "page_size": 10,
            "use_cache": True
        }
    }
}
