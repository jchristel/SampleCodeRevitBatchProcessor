# test data for single and multiple family report tests
# family base data
# 5 families:
# 1. Sample_Family_Eight (Sample_Family_Eight)
# 2. Sample_Family_Thirteen (Sample_Family_Eight :: Sample_Family_Thirteen)
# 3. Sample_Family_Ten (Sample_Family_Ten)
# 4. Sample_Family_Six (Sample_Family_Six)
# 5. Sample_Family_Thirteen (Sample_Family_Six :: Sample_Family_Thirteen)

TEST_DATA_FAMILY_BASE = [
    [
        [
            "FamilyBase",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
        ],
        [
            "FamilyBase",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
        ],
        [
            "FamilyBase",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
        ],
        [
            "FamilyBase",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
        ],
        [
            "FamilyBase",
            "Sample_Family_Six :: Sample_Family_Thirteen",
            "Specialty Equipment :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
        ],
    ]
]

# family categories,
# 3 families:
# 1. Sample_Family_Eight (Sample_Family_Eight)
# 2. Sample_Family_Thirteen (Sample_Family_Eight :: Sample_Family_Thirteen)
# 3. Sample_Family_Ten (Sample_Family_Ten)

TEST_DATA_FAMILY_CATEGORIES = (
    [
        [
            "Category",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "1",
            [
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 10601223,
                }
            ],
            "Furniture Systems",
            "Fixed Furniture",
            "3674407",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "1",
            "0",
            "0",
            "0",
        ],
        [
            "Category",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "0",
            "None",
            "Furniture Systems",
            "<Hidden Lines>",
            "-2009518",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "3",
            "0",
            "0",
            "0",
        ],
        [
            "Category",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "0",
            "None",
            "Section Marks",
            "<Wide Lines>",
            "-2000404",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "3",
            "0",
            "0",
            "0",
        ],
        [
            "Category",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "0",
            "None",
            "Section Marks",
            "<Medium Lines>",
            "-2000403",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "3",
            "0",
            "0",
            "0",
        ],
        [
            "Category",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "4",
            [
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Thirteen",
                    "element_id": 10600645,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Thirteen",
                    "element_id": 10600646,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Thirteen",
                    "element_id": 10600647,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Thirteen",
                    "element_id": 10600648,
                },
            ],
            "Section Marks",
            "<Thin Lines>",
            "-2000401",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "1",
            "0",
            "0",
            "0",
        ],
        [
            "Category",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "14",
            [
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156354,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156355,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156356,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156369,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156370,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156371,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156372,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156373,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156374,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156375,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156376,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156377,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156378,
                },
                {
                    "data_type": "FamilyCategoryDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": 9156379,
                },
            ],
            "Generic Annotations",
            "Generic Annotation_Ceiling Only",
            "1639988",
            "None",
            "None",
            "None",
            "None",
            "-1",
            "None",
            "5",
            "0",
            "0",
            "0",
        ],
    ],
)

# family line patterns
# 4 families:
# 1. Sample_Family_Eight (Sample_Family_Eight)
# 2. Sample_Family_Thirteen (Sample_Family_Eight :: Sample_Family_Thirteen)
# 3. Sample_Family_Ten (Sample_Family_Ten)
# 4. Sample_Family_Six (Sample_Family_Six)

TEST_DATA_FAMILY_LINE_PATTERNS = (
    [
        [
            "LinePattern",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": -2009518,
                }
            ],
            "Hidden 04_BVN",
            "1428068",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "2",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                    "element_id": -2000530,
                },
            ],
            "Reference Plane 02_BVN",
            "1428069",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "2",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                    "element_id": -2000083,
                },
            ],
            "Dash 06_BVN",
            "1436489",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 10600768,
                }
            ],
            "Dash dot",
            "1499753",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "0",
            "None",
            "Hidden 04_BVN",
            "1428068",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                    "element_id": -2000530,
                }
            ],
            "Reference Plane 02_BVN",
            "1428069",
        ],
        [
            "LinePattern",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                    "element_id": -2000083,
                }
            ],
            "Dash 06_BVN",
            "1436489",
        ],
        [
            "LinePattern",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "0",
            "None",
            "Hidden 04_BVN",
            "1428068",
        ],
        [
            "LinePattern",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": -2000530,
                }
            ],
            "Reference Plane 02_BVN",
            "1428069",
        ],
        [
            "LinePattern",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "1",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Ten",
                    "element_id": -2000083,
                }
            ],
            "Dash 06_BVN",
            "1436489",
        ],
        [
            "LinePattern",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "3",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": -2009527,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": -2009512,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": -2009517,
                },
            ],
            "Hidden 04_BVN",
            "1428068",
        ],
        [
            "LinePattern",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "9",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Thirteen",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN",
                    "element_id": -2000530,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN",
                    "element_id": -2000530,
                },
            ],
            "Reference Plane 02_BVN",
            "1428069",
        ],
        [
            "LinePattern",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "9",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Thirteen",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN",
                    "element_id": -2000083,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN",
                    "element_id": -2000083,
                },
            ],
            "Dash 06_BVN",
            "1436489",
        ],
        [
            "LinePattern",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "3",
            [
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 8485759,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": 9152387,
                },
                {
                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 9156917,
                },
            ],
            "Dash dot",
            "1499753",
        ],
    ],
)

# family shared parameters
# 4 families:
# 1. Sample_Family_Eight (Sample_Family_Eight)
# 2. Sample_Family_Thirteen (Sample_Family_Eight :: Sample_Family_Thirteen)
# 3. Sample_Family_Ten (Sample_Family_Ten)
# 4. Sample_Family_Six (Sample_Family_Six)

TEST_DATA_FAMILY_SHARED_PARAMETERS = (
    [
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "94e25b89-289e-43d7-bba9-c1c23be396e9",
            "Author",
            "118408",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 118408,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
            "ItemCode",
            "1640398",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1640398,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
            "ItemDescription",
            "1640399",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1640399,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "be50f510-c92c-4c52-9dcf-b152201710df",
            "ItemGroup",
            "1640401",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1640401,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "1d88889c-80d2-4aad-acbe-11076796e986",
            "Copyright",
            "1642131",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1642131,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "0e397bbd-a378-4824-b08a-3c03423f5545",
            "HEIGHT_BVN",
            "1642132",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1642132,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "980aef7a-c409-4f02-acb2-895aed435f26",
            "DEPTH_BVN",
            "1642133",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1642133,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "10fc5a92-3d94-4deb-b74a-23825ebce640",
            "WIDTH_BVN",
            "1642135",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1642135,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "6a99c82d-821c-4726-8c75-a4e0097f4441",
            "DetailedCategory",
            "1698538",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698538,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "a65f6d59-9c87-44bc-866b-5644e8412a3f",
            "ModifiedIssue",
            "1698539",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698539,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
            "Responsibility",
            "1698541",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698541,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
            "UniqueID",
            "1698542",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698542,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
            "MOUNTING_HEIGHT_TOP_BVN",
            "1698543",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698543,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "f074bc9a-c650-42f4-aeb1-29de0255343f",
            "MOUNTING_HEIGHT_US_BVN",
            "1698544",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1698544,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
            "CEILING_HEIGHT_BVN",
            "1721566",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Eight",
                    "element_id": 1721566,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "",
            "No shared parameter present in family.",
            "-1",
            "0",
            "None",
        ],
        [
            "SharedParameter",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "",
            "No shared parameter present in family.",
            "-1",
            "0",
            "None",
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "94e25b89-289e-43d7-bba9-c1c23be396e9",
            "Author",
            "118408",
            "3",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 118408,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": 118408,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 118408,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
            "ItemCode",
            "1640398",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1640398,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1640398,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
            "ItemDescription",
            "1640399",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1640399,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1640399,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "be50f510-c92c-4c52-9dcf-b152201710df",
            "ItemGroup",
            "1640401",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1640401,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1640401,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "1d88889c-80d2-4aad-acbe-11076796e986",
            "Copyright",
            "1642131",
            "3",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1642131,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": 1642131,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1642131,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "0e397bbd-a378-4824-b08a-3c03423f5545",
            "HEIGHT_BVN",
            "1642132",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1642132,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1642132,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "980aef7a-c409-4f02-acb2-895aed435f26",
            "DEPTH_BVN",
            "1642133",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1642133,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1642133,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "10fc5a92-3d94-4deb-b74a-23825ebce640",
            "WIDTH_BVN",
            "1642135",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1642135,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1642135,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "6a99c82d-821c-4726-8c75-a4e0097f4441",
            "DetailedCategory",
            "1698538",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1698538,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1698538,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "a65f6d59-9c87-44bc-866b-5644e8412a3f",
            "ModifiedIssue",
            "1698539",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1698539,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1698539,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
            "Responsibility",
            "1698541",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1698541,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1698541,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
            "UniqueID",
            "1698542",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1698542,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1698542,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
            "CEILING_HEIGHT_BVN",
            "1721566",
            "2",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six",
                    "element_id": 1721566,
                },
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 1721566,
                },
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "b74b295e-c1e3-4d7d-b98a-29a1af08d12d",
            "Modified Issue",
            "9133881",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                    "element_id": 9133881,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "3f3f6ed3-c88f-443e-a0b0-b09bbb067881",
            "MOUNTING_HEIGHT_CENTRE_BVN",
            "9133882",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 9133882,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
            "MOUNTING_HEIGHT_TOP_BVN",
            "9133883",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 9133883,
                }
            ],
        ],
        [
            "SharedParameter",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "f074bc9a-c650-42f4-aeb1-29de0255343f",
            "MOUNTING_HEIGHT_US_BVN",
            "9133884",
            "1",
            [
                {
                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                    "element_id": 9133884,
                }
            ],
        ],
    ],
)

# family warnings
# 5 families:
# 1. Sample_Family_Eight (Sample_Family_Eight)
# 2. Sample_Family_Thirteen (Sample_Family_Eight :: Sample_Family_Thirteen)
# 3. Sample_Family_Ten (Sample_Family_Ten)
# 4. Sample_Family_Six (Sample_Family_Six)
# 5. Sample_Family_Thirteen (Sample_Family_Six :: Sample_Family_Thirteen)

TEST_DATA_FAMILY_WARNINGS = [
    [
        [
            "Warnings",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            "No warnings present in family.",
            "",
            "None",
            "None",
        ],
        [
            "Warnings",
            "Sample_Family_Eight :: Sample_Family_Thirteen",
            "Furniture Systems :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "No warnings present in family.",
            "",
            "None",
            "None",
        ],
        [
            "Warnings",
            "Sample_Family_Ten",
            "Generic Annotations",
            "Sample_Family_Ten",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
            "No warnings present in family.",
            "",
            "None",
            "None",
        ],
        [
            "Warnings",
            "Sample_Family_Six",
            "Specialty Equipment",
            "Sample_Family_Six",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
            "No warnings present in family.",
            "",
            "None",
            "None",
        ],
        [
            "Warnings",
            "Sample_Family_Six :: Sample_Family_Thirteen",
            "Specialty Equipment :: Section Marks",
            "Sample_Family_Thirteen",
            "-",
            "No warnings present in family.",
            "",
            "None",
            "None",
        ],
    ]
]

# all test data as a list
TEST_DATA_ALL = (
    TEST_DATA_FAMILY_BASE,
    TEST_DATA_FAMILY_CATEGORIES,
    TEST_DATA_FAMILY_LINE_PATTERNS,
    TEST_DATA_FAMILY_SHARED_PARAMETERS,
    TEST_DATA_FAMILY_WARNINGS,
)

def build_data_dict_all():
    """
    Build a dictionary from the test data where the key is the family nesting path and the value is a dictionary where the key is the data storage name and the value is a list of storage instances.
    
    :return: dict
    :rtype: dict
    """
    
    # returns a dictionary where key is the family nesting path and value is
    # a dictionary where key is the data storage name and value is the list of storage instances

    data_dict = {}
    for data in TEST_DATA_ALL:
        for family_data in data[0]:
            family_nesting_path = family_data[1]
            data_storage_name = family_data[0]
            data_storage_instances = family_data

            if family_nesting_path not in data_dict:
                data_dict[family_nesting_path] = {}

            if data_storage_name not in data_dict[family_nesting_path]:
                data_dict[family_nesting_path][data_storage_name] = []

            data_dict[family_nesting_path][data_storage_name].append(data_storage_instances)
    
    return data_dict
