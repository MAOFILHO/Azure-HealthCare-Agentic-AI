# QA v1 issue 33 @ 5f261bd
$ pytest -q
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 9.74s

Mutation 1: print rg-northfield-ai -> test_cleanup_prints_the_group_name_that_destroy_sh_deletes FAILED (1 failed, 5 passed), restored
Mutation 2: destroy.sh group="other-rg" -> same test FAILED (1 failed, 5 passed), restored
Restored: pytest 73 passed
