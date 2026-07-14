using ECCD.Application.Auth.Commands;
using ECCD.Application.Common.Models;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

public class AuthController : ApiControllerBase
{
    [HttpPost("register/teacher")]
    public async Task<ActionResult<ApiResponse<string>>> RegisterTeacher(RegisterTeacherCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<string>.Fail("REGISTRATION_FAILED", result.Error ?? "Failed to register teacher.", result.Errors));
        }
        return Ok(ApiResponse<string>.Success(result.Data!));
    }

    [HttpPost("register/parent")]
    public async Task<ActionResult<ApiResponse<string>>> RegisterParent(RegisterParentCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<string>.Fail("REGISTRATION_FAILED", result.Error ?? "Failed to register parent.", result.Errors));
        }
        return Ok(ApiResponse<string>.Success(result.Data!));
    }

    [HttpPost("login")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> Login(LoginCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return Unauthorized(ApiResponse<LoginResponse>.Fail("UNAUTHORIZED", result.Error ?? "Invalid username or password."));
        }
        return Ok(ApiResponse<LoginResponse>.Success(result.Data!));
    }

    [HttpPost("forgot-password")]
    public async Task<ActionResult<ApiResponse<string>>> ForgotPassword(ForgotPasswordCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<string>.Fail("FORGOT_PASSWORD_FAILED", result.Error ?? "Request failed."));
        }
        return Ok(ApiResponse<string>.Success("If the email exists, a verification code has been sent."));
    }

    [HttpPost("reset-password")]
    public async Task<ActionResult<ApiResponse<string>>> ResetPassword(ResetPasswordCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<string>.Fail("RESET_PASSWORD_FAILED", result.Error ?? "Password reset failed.", result.Errors));
        }
        return Ok(ApiResponse<string>.Success("Password reset succeeded. You can now login."));
    }
}
