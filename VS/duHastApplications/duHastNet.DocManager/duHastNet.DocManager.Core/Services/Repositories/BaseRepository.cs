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
/// Base repository implementation using sqlite-net-pcl
/// </summary>
public abstract class BaseRepository<T> : IRepository<T> where T : class, new()
{
    protected readonly SQLiteAsyncConnection _connection;

    protected BaseRepository(SQLiteAsyncConnection connection)
    {
        _connection = connection;
    }

    public virtual async Task<T?> GetByIdAsync(int id)
    {
        return await _connection.FindAsync<T>(id).ConfigureAwait(false);
    }

    public virtual async Task<List<T>> GetAllAsync()
    {
        return await _connection.Table<T>().ToListAsync().ConfigureAwait(false);
    }

    public virtual async Task<List<T>> FindAsync(Expression<Func<T, bool>> predicate)
    {
        return await _connection.Table<T>().Where(predicate).ToListAsync().ConfigureAwait(false);
    }

    public virtual async Task<T?> FirstOrDefaultAsync(Expression<Func<T, bool>> predicate)
    {
        return await _connection.Table<T>().Where(predicate).FirstOrDefaultAsync().ConfigureAwait(false);
    }

    public virtual async Task<int> InsertAsync(T entity)
    {
        return await _connection.InsertAsync(entity).ConfigureAwait(false);
    }

    public virtual async Task<int> UpdateAsync(T entity)
    {
        return await _connection.UpdateAsync(entity).ConfigureAwait(false);
    }

    public virtual async Task<int> DeleteAsync(T entity)
    {
        return await _connection.DeleteAsync(entity).ConfigureAwait(false);
    }

    public virtual async Task<int> DeleteAsync(int id)
    {
        return await _connection.DeleteAsync<T>(id).ConfigureAwait(false);
    }

    public virtual async Task<int> CountAsync()
    {
        return await _connection.Table<T>().CountAsync().ConfigureAwait(false);
    }

    public virtual async Task<int> CountAsync(Expression<Func<T, bool>> predicate)
    {
        return await _connection.Table<T>().Where(predicate).CountAsync().ConfigureAwait(false);
    }

    public virtual async Task<bool> ExistsAsync(Expression<Func<T, bool>> predicate)
    {
        var count = await CountAsync(predicate).ConfigureAwait(false);
        return count > 0;
    }

    public virtual async Task<int> InsertAllAsync(IEnumerable<T> entities)
    {
        return await _connection.InsertAllAsync(entities).ConfigureAwait(false);
    }

    public virtual async Task<int> UpdateAllAsync(IEnumerable<T> entities)
    {
        return await _connection.UpdateAllAsync(entities).ConfigureAwait(false);
    }

    public virtual async Task<int> DeleteAllAsync(IEnumerable<T> entities)
    {
        var count = 0;
        foreach (var entity in entities)
        {
            count += await DeleteAsync(entity).ConfigureAwait(false);
        }
        return count;
    }
}