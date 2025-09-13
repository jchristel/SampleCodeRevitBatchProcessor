//
//License:
//
//
// Revit Batch Processor Sample Code
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

using System.Linq.Expressions;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Generic repository interface for basic CRUD operations
/// </summary>
public interface IRepository<T> where T : class, new()
{
    /// <summary>
    /// Gets an entity by its ID
    /// </summary>
    Task<T?> GetByIdAsync(int id);

    /// <summary>
    /// Gets all entities of type T
    /// </summary>
    Task<List<T>> GetAllAsync();

    /// <summary>
    /// Finds entities matching the specified predicate
    /// </summary>
    Task<List<T>> FindAsync(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Gets the first entity matching the predicate, or null if not found
    /// </summary>
    Task<T?> FirstOrDefaultAsync(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Inserts a new entity
    /// </summary>
    Task<int> InsertAsync(T entity);

    /// <summary>
    /// Updates an existing entity
    /// </summary>
    Task<int> UpdateAsync(T entity);

    /// <summary>
    /// Deletes the specified entity
    /// </summary>
    Task<int> DeleteAsync(T entity);

    /// <summary>
    /// Deletes an entity by its ID
    /// </summary>
    Task<int> DeleteAsync(int id);

    /// <summary>
    /// Gets the total count of entities
    /// </summary>
    Task<int> CountAsync();

    /// <summary>
    /// Gets the count of entities matching the predicate
    /// </summary>
    Task<int> CountAsync(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Checks if any entity matches the predicate
    /// </summary>
    Task<bool> ExistsAsync(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Inserts multiple entities in a batch operation
    /// </summary>
    Task<int> InsertAllAsync(IEnumerable<T> entities);

    /// <summary>
    /// Updates multiple entities in a batch operation
    /// </summary>
    Task<int> UpdateAllAsync(IEnumerable<T> entities);

    /// <summary>
    /// Deletes multiple entities in a batch operation
    /// </summary>
    Task<int> DeleteAllAsync(IEnumerable<T> entities);
}