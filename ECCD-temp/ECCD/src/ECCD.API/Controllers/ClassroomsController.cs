using ECCD.Application.Classrooms.Commands;
using ECCD.Application.Classrooms.Queries;
using ECCD.Application.Common.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

[Authorize]
public class ClassroomsController : ApiControllerBase
{
    [HttpPost]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<Guid>>> Create(CreateClassroomCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<Guid>.Fail("CREATE_CLASSROOM_FAILED", result.Error ?? "Failed to create classroom."));
        }
        return Ok(ApiResponse<Guid>.Success(result.Data!));
    }

    [HttpGet]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<List<ClassroomDto>>>> GetTeacherClassrooms()
    {
        var result = await Mediator.Send(new GetTeacherClassroomsQuery());
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<List<ClassroomDto>>.Fail("GET_CLASSROOMS_FAILED", result.Error ?? "Failed to load classrooms."));
        }
        return Ok(ApiResponse<List<ClassroomDto>>.Success(result.Data!));
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<ApiResponse<ClassroomDto>>> GetById(Guid id)
    {
        var result = await Mediator.Send(new GetClassroomByIdQuery(id));
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<ClassroomDto>.Fail("GET_CLASSROOM_FAILED", result.Error ?? "Failed to load classroom."));
        }
        return Ok(ApiResponse<ClassroomDto>.Success(result.Data!));
    }

    [HttpPut("{id}")]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<object>>> Update(Guid id, UpdateClassroomCommand command)
    {
        if (id != command.Id)
        {
            return BadRequest(ApiResponse<object>.Fail("BAD_REQUEST", "Parameter ID does not match body ID."));
        }

        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<object>.Fail("UPDATE_CLASSROOM_FAILED", result.Error ?? "Failed to update classroom."));
        }
        return Ok(ApiResponse<object>.Success(null!));
    }

    [HttpDelete("{id}")]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<object>>> Archive(Guid id)
    {
        var result = await Mediator.Send(new ArchiveClassroomCommand(id));
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<object>.Fail("ARCHIVE_CLASSROOM_FAILED", result.Error ?? "Failed to archive classroom."));
        }
        return Ok(ApiResponse<object>.Success(null!));
    }
}
