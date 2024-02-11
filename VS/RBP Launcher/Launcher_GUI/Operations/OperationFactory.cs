using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Windows;

namespace Launcher_GUI
{
    public static class OperationFactory
    {
        public static List<ViewModels.OperationInfoViewModel> GetOperationsInfo(Type container)
        {
            List<ViewModels.OperationInfoViewModel> result = new List<ViewModels.OperationInfoViewModel>();

            foreach (var method in container.GetMethods())
            {
                if (method.IsStatic)
                {
                    ViewModels.OperationInfoViewModel op = new ViewModels.OperationInfoViewModel
                    {
                        Title = method.Name
                    };

                    var attr = method.GetCustomAttribute<OperationAttribute>();
                    var para = method.GetParameters();

                    bool generateInputNames = true;

                    //op.Type = OperationType.Normal;

                    //if (para.Length == 2)
                    //{
                    //    var delType = typeof(Func<double, double, double>);
                    //    var del = (Func<double, double, double>)Delegate.CreateDelegate(delType, method);

                    //    op.Operation = new BinaryOperation(del);
                    //}
                    //else if (para.Length == 1)
                    //{
                    //    if (para[0].ParameterType.IsArray)
                    //    {
                    //        op.Type = OperationType.Expando;

                    //        var delType = typeof(Func<double[], double>);
                    //        var del = (Func<double[], double>)Delegate.CreateDelegate(delType, method);

                    //        op.Operation = new ParamsOperation(del);
                    //        op.MaxInput = int.MaxValue;
                    //    }
                    //    else
                    //    {
                    //        var delType = typeof(Func<double, double>);
                    //        var del = (Func<double, double>)Delegate.CreateDelegate(delType, method);

                    //        op.Operation = new UnaryOperation(del);
                    //    }
                    //}
                    //else if (para.Length == 0)
                    //{
                    //    var delType = typeof(Func<double>);
                    //    var del = (Func<double>)Delegate.CreateDelegate(delType, method);

                    //    op.Operation = new ValueOperation(del);
                    //}

                    if (attr != null)
                    {
                        op.MinInput = attr.MinInput;
                        op.MaxInput = attr.MaxInput;
                        generateInputNames = attr.GenerateInputNames;
                    }
                    else
                    {
                        op.MinInput = (uint)para.Length;
                        op.MaxInput = (uint)para.Length;
                    }

                    foreach (var param in para)
                    {
                        op.Input.Add(generateInputNames ? param.Name : null);
                    }

                    for (int i = op.Input.Count; i < op.MinInput; i++)
                    {
                        op.Input.Add(null);
                    }

                    result.Add(op);
                }
            }

            return result;
        }

        public static ViewModels.OperationViewModel GetOperation(ViewModels.OperationInfoViewModel info)
        {
            var input = info.Input.Select(i => new ViewModels.ConnectorViewModel
            {
                Title = i
            });

            switch (info.Type)
            {
                //case ViewModels.OperationType.Expression:
                //    return new ExpressionOperationViewModel
                //    {
                //        Title = info.Title,
                //        Output = new ViewModels.ConnectorViewModel(),
                //        Operation = info.Operation,
                //        Expression = "1 + sin {a} + cos {b}"
                //    };

                case ViewModels.OperationType.Calculator:
                    return new ViewModels.CalculatorOperationViewModel
                    {
                        Title = info.Title,
                        Operation = info.Operation,
                    };

                case ViewModels.OperationType.Expando:
                    var o = new ViewModels.ExpandoOperationViewModel
                    {
                        MaxInput = info.MaxInput,
                        MinInput = info.MinInput,
                        Title = info.Title,
                        Output = new ViewModels.ConnectorViewModel(),
                        Operation = info.Operation
                    };

                    o.Input.AddRange(input);
                    return o;

                case ViewModels.OperationType.Group:
                    return new ViewModels.OperationGroupViewModel
                    {
                        Title = info.Title,
                    };

                case ViewModels.OperationType.Graph:
                    return new ViewModels.OperationGraphViewModel
                    {
                        Title = info.Title,
                        DesiredSize = new Size(420, 250)
                    };

                default:
                    {
                        var op = new ViewModels.OperationViewModel
                        {
                            Title = info.Title,
                            Output = new ViewModels.ConnectorViewModel(),
                            Operation = info.Operation
                        };

                        op.Input.AddRange(input);
                        return op;
                    }
            }
        }
    }
}
