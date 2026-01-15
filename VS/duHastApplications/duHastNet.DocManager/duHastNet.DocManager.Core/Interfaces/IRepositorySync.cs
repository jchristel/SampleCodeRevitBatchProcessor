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

using System.Linq.Expressions;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Base synchronous repository interface for CRUD operations.
/// Provides synchronous database access for IronPython/PyRevit compatibility.
/// Mirrors the async IRepository<T> interface with synchronous methods.
/// </summary>
/// <typeparam name="T">Entity type</typeparam>
public interface IRepositorySync<T> where T : class
{
    /// <summary>
    /// Gets an entity by its ID (sync version)
    /// </summary>
    /// <param name="id">Entity ID</param>
    /// <returns>Entity if found, null otherwise</returns>
    T? GetById(int id);

    /// <summary>
    /// Gets all entities (sync version)
    /// </summary>
    /// <returns>List of all entities</returns>
    List<T> GetAll();

    /// <summary>
    /// Finds entities matching the specified predicate (sync version)
    /// </summary>
    /// <param name="predicate">Expression to filter entities</param>
    /// <returns>List of matching entities</returns>
    List<T> Find(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Gets the first entity matching the predicate, or null if not found (sync version)
    /// </summary>
    /// <param name="predicate">Expression to filter entities</param>
    /// <returns>First matching entity or null</returns>
    T? FirstOrDefault(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Inserts a new entity (sync version)
    /// </summary>
    /// <param name="entity">Entity to insert</param>
    /// <returns>Number of rows affected</returns>
    int Insert(T entity);

    /// <summary>
    /// Updates an existing entity (sync version)
    /// </summary>
    /// <param name="entity">Entity to update</param>
    /// <returns>Number of rows affected</returns>
    int Update(T entity);

    /// <summary>
    /// Deletes an entity (sync version)
    /// </summary>
    /// <param name="entity">Entity to delete</param>
    /// <returns>Number of rows affected</returns>
    int Delete(T entity);

    /// <summary>
    /// Deletes an entity by its ID (sync version)
    /// </summary>
    /// <param name="id">Entity ID</param>
    /// <returns>Number of rows affected</returns>
    int Delete(int id);

    /// <summary>
    /// Gets the count of all entities (sync version)
    /// </summary>
    /// <returns>Total count</returns>
    int Count();

    /// <summary>
    /// Gets the count of entities matching the predicate (sync version)
    /// </summary>
    /// <param name="predicate">Expression to filter entities</param>
    /// <returns>Count of matching entities</returns>
    int Count(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Checks if any entity matches the predicate (sync version)
    /// </summary>
    /// <param name="predicate">Expression to filter entities</param>
    /// <returns>True if any entity matches, false otherwise</returns>
    bool Exists(Expression<Func<T, bool>> predicate);

    /// <summary>
    /// Inserts multiple entities in a batch operation (sync version)
    /// </summary>
    /// <param name="entities">Entities to insert</param>
    /// <returns>Number of rows affected</returns>
    int InsertAll(IEnumerable<T> entities);

    /// <summary>
    /// Updates multiple entities in a batch operation (sync version)
    /// </summary>
    /// <param name="entities">Entities to update</param>
    /// <returns>Number of rows affected</returns>
    int UpdateAll(IEnumerable<T> entities);

    /// <summary>
    /// Deletes multiple entities in a batch operation (sync version)
    /// </summary>
    /// <param name="entities">Entities to delete</param>
    /// <returns>Number of rows affected</returns>
    int DeleteAll(IEnumerable<T> entities);
}
