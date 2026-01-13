//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using SQLite;
using duHastNet.DocManager.Core.Interfaces;
using System.Linq.Expressions;

namespace duHastNet.DocManager.Core.Services.Repositories;

/// <summary>
/// Base synchronous repository implementation using sqlite-net-pcl.
/// Provides synchronous database access for IronPython/PyRevit compatibility.
/// </summary>
public abstract class BaseRepositorySync<T> : IRepositorySync<T> where T : class, new()
{
    protected readonly SQLiteConnection _connection;

    protected BaseRepositorySync(SQLiteConnection connection)
    {
        _connection = connection ?? throw new ArgumentNullException(nameof(connection));
    }

    public virtual T? GetById(int id)
    {
        return _connection.Find<T>(id);
    }

    public virtual List<T> GetAll()
    {
        return _connection.Table<T>().ToList();
    }

    public virtual List<T> Find(Expression<Func<T, bool>> predicate)
    {
        return _connection.Table<T>().Where(predicate).ToList();
    }

    public virtual T? FirstOrDefault(Expression<Func<T, bool>> predicate)
    {
        return _connection.Table<T>().Where(predicate).FirstOrDefault();
    }

    public virtual int Insert(T entity)
    {
        return _connection.Insert(entity);
    }

    public virtual int Update(T entity)
    {
        return _connection.Update(entity);
    }

    public virtual int Delete(T entity)
    {
        return _connection.Delete(entity);
    }

    public virtual int Delete(int id)
    {
        return _connection.Delete<T>(id);
    }

    public virtual int Count()
    {
        return _connection.Table<T>().Count();
    }

    public virtual int Count(Expression<Func<T, bool>> predicate)
    {
        return _connection.Table<T>().Where(predicate).Count();
    }

    public virtual bool Exists(Expression<Func<T, bool>> predicate)
    {
        var count = Count(predicate);
        return count > 0;
    }

    public virtual int InsertAll(IEnumerable<T> entities)
    {
        return _connection.InsertAll(entities);
    }

    public virtual int UpdateAll(IEnumerable<T> entities)
    {
        return _connection.UpdateAll(entities);
    }

    public virtual int DeleteAll(IEnumerable<T> entities)
    {
        var count = 0;
        foreach (var entity in entities)
        {
            count += Delete(entity);
        }
        return count;
    }
}
